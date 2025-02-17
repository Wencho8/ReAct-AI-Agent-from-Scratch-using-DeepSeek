import os
from dotenv import load_dotenv
import re
from openai import OpenAI
from transformers import AutoTokenizer
from AgentTools.wiki import Wiki
from AgentTools.web_searcher import Searcher
from AgentTools.weather import Weather
from Utils.utils import Message
from datetime import datetime
import random
import time



def timeit(func):
    """Decorator to measure and print the execution time of a function."""
    def timed(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function {func.__name__} took {end_time - start_time:.4f} seconds. ⏱️")
        return result
    return timed



class Agent:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL")
        )
        self.model_name = "deepseek-ai/DeepSeek-V3"
        self.tools = {}
        self.messages = []
        self.max_iterations = 5
        self.current_iteration = 0
        self.system_prompt = self.load_prompt("Prompts/system_prompt.txt")
        self.old_chats_summary = ""
        self.messages_to_summarize = 5
        self.max_messages_tokens = 10000
        self.summary_prompt = self.load_prompt("Prompts/summary_prompt.txt")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, cache_dir="./tokenizer_cache")

    def register_tool(self, tool):
        """Registers a tool by its name."""
        self.tools[tool.name.lower()] = tool
    
    def get_tools(self):
        """Returns a formatted string listing available tools."""
        return "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools.values()])

    def add_message(self, role, content):
        """Add a message to the messages list."""
        self.messages.append(Message(role=role, content=content))

    def get_chat_history(self):
        """Return the chat history as a list of message dictionaries."""
        return [
            {
                "role": message.role,
                "content": message.content,
                **({"tool_call_id": random.randint(1, 1000)} if message.role == "tool" else {})
            }
            for message in self.messages
        ]

    def load_prompt(self, path):
        """Returns a prompt from a file."""
        with open(path, "r") as file:
            return file.read() if file else ""

    def summarize_old_chats(self, lines):
        """Summarizes old chat history and returns a concise summary response."""
        prompt = self.summary_prompt.format(lines=lines)

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],  ## If you are using gpt you could use system here.
            max_tokens=120,
        )

        return response.choices[0].message.content.strip() if response.choices else "No response from DeepSeek"

    def extract_first_queries(self, chat_history):
        """Extracts a specified number of consecutive user queries from the given chat history."""
        user_indices = [i for i, msg in enumerate(chat_history) if msg["role"] == "user"]

        start_index = user_indices[0]
        end_index = user_indices[self.messages_to_summarize]

        return start_index, end_index

    @timeit
    def num_tokens_from_messages(self, messages):
        """Return the number of tokens used by a list of messages"""
        value = self.tokenizer.apply_chat_template(messages, tokenize=False)
        encoded = self.tokenizer.encode(value)
        
        return len(encoded)
    
    def num_tokens_from_text(self, text):
        """Return the number of tokens used by the given text."""
        encoded = self.tokenizer.encode(text)

        return len(encoded)

    @timeit
    def think(self):
        """Think and decide based on the response from DeepSeek."""
        self.current_iteration += 1

        if self.current_iteration > self.max_iterations:
            print("Reached maximum iterations. Stopping.")
            self.add_message("assistant", "I'm sorry, but I couldn't find a satisfactory answer within the allowed number of iterations.")
            return
        
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prompt = self.system_prompt.format(
            tools=self.get_tools(),
            date=current_date
        )
        response = self.call_DeepSeek(prompt)
        self.add_message("assistant", response)
        self.decide(response)

    @timeit
    def decide(self, response):
        """Decide on the next action based on the response."""
        final_answer_match = re.search(r"Final Answer:", response)
        if final_answer_match:
            return

        action_match = re.search(r"Action:\s*(\w+):\s*(.*)", response)
        if action_match:
            tool_name = action_match.group(1).strip().lower()
            query = action_match.group(2).strip()
            self.act(tool_name, query)

        if not final_answer_match and not action_match:
            print("No action or final answer found in the response.")

    @timeit
    def act(self, tool_name, query):
        """Act on the response by calling the appropriate tool."""
        tool = self.tools.get(tool_name)

        if tool:
            result = tool.use(query)
            observation = f"Observation from {tool_name}: {result}"
            self.add_message("tool", observation)                   ## If you are using gpt you could simply use system here.
            self.think()
        else:
            print(f"No tool registered for choice: {tool_name}")
            self.add_message("system", f"Error: Tool {tool_name} not found")
    
    @timeit
    def memory_management(self, chat_history):
        """Manages memory by summarizing and deleting old chat history"""
        try:
            user_messages = [msg for msg in chat_history if msg["role"] == "user"]
            if len(user_messages) > self.messages_to_summarize and self.num_tokens_from_messages(chat_history) > self.max_messages_tokens:
                indices = self.extract_first_queries(chat_history)
                if indices:
                    start_index, end_index = indices
                    lines = chat_history[start_index:end_index]
                    print(f"Tokens used by the conversation to summarize: {self.num_tokens_from_messages(lines)}")
                    new_summary = self.summarize_old_chats(lines)
                    if new_summary != "No response from DeepSeek":
                        print(f"Tokens used by the new summary: {self.num_tokens_from_text(new_summary)}")
                        self.old_chats_summary = f"{self.old_chats_summary} {new_summary}".strip()
                        del self.messages[start_index:end_index]
        except Exception as e:
            print(f"An error occurred during memory management: {e}")
 
    @timeit
    def call_DeepSeek(self, prompt):
        """Call the DeepSeek API to get a response."""
        chat_history = self.get_chat_history()
        
        self.memory_management(chat_history)

        if self.old_chats_summary:
            prompt += f"\n\nOld messages summary:\n{self.old_chats_summary}"
        
        messages = [{"role": "system", "content": prompt}] + chat_history

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=500,
            temperature=0.5,
        )

        return response.choices[0].message.content.strip() if response.choices else "No response from DeepSeek"

    def execute(self, query):
        """Execute a user query and return the full Agent response."""
        self.current_iteration = 0
        self.add_message("user", query)
        self.think()
        
        result_messages = []
        for message in self.messages[::-1]:
            if message.role == "user":
                break
            elif message.role != "user":
                result_messages.append(message)

        return result_messages[::-1]



## Tested as a standalone script
if __name__ == "__main__":
    from colorama import Fore, Style, init
    init(autoreset=True)
    agent = Agent()

    # Register tools directly using their instances
    for tool in [Wiki(), Searcher(), Weather()]:
        agent.register_tool(tool)

    while True:
        query = input(f"{Fore.CYAN}USER:{Style.RESET_ALL} ").strip()
        if query.lower() in ["exit", "quit"]:
            print(f"{Fore.YELLOW}Exiting the agent. Goodbye!{Style.RESET_ALL}")
            break
        
        result = agent.execute(query)

        role_colors = {
            "tool": Fore.MAGENTA,
            "assistant": Fore.GREEN,
        }

        for message in result:
            role_color = role_colors.get(message.role, Fore.WHITE)
            content = message.content

            if "Final Answer:" in content:
                content = content.replace("Final Answer:", f"{Fore.RED}--Final Answer:{Style.RESET_ALL}")

            print(f"{role_color}{message.role.upper()}:{Style.RESET_ALL} {content}")

        print("\n")