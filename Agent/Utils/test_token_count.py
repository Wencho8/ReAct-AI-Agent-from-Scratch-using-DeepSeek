import os
from dotenv import load_dotenv
from transformers import AutoTokenizer
from openai import OpenAI

load_dotenv()

openai = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL")
)

model_name = "deepseek-ai/DeepSeek-V3"
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="./tokenizer_cache")


def num_tokens_from_content(messages):
    """Return the total number of tokens used by the content in a list of messages"""
    return sum(len(tokenizer.encode(message["content"])) for message in messages if "content" in message)


def num_tokens_from_messages(messages):
    """Return the number of tokens used by a list of messages in DeepSeek-V3."""
    value = tokenizer.apply_chat_template(messages, tokenize=False)
    print(f"Messages with template: {value}")
    encoded = tokenizer.encode(value)
    return len(encoded)


example_messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, how are you?"},
    {"role": "assistant", "content": "I'm just a bot, but I'm here to help!"},
    {"role": "user", "content": "What can you do?"},
]


## Tokens from just the content of the messages
print(f"Token count from the content of the messages: {num_tokens_from_content(example_messages)}")

## Tokens from the messages:
print(f"Token count from the messages: {num_tokens_from_messages(example_messages)}")


# Real Prompt token usage when calling the API
chat_completion = openai.chat.completions.create(
    model="deepseek-ai/DeepSeek-V3",
    messages=example_messages
)
print(f"Token count from the prompt when calling the API: {chat_completion.usage.prompt_tokens}")