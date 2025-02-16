import streamlit as st
import requests

# FastAPI URL
FASTAPI_URL = "http://127.0.0.1:8000/chat"

# Streamlit UI
st.title("ReAct Agent Chat")

with st.sidebar:
    st.title("Current Chain of Thought")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Function to display chat messages in the main chat
def display_message(role, content):
    with st.chat_message(role):
        st.markdown(content)

# Function to classify messages into sidebar or main chat
def process_messages(messages):
    sidebar_messages = []
    main_messages = []
    final_answer = None

    for message in messages:
        role = message["role"]
        content = message["content"]

        # Extract final answer if present
        if "Final Answer:" in content:
            final_answer = content.split("Final Answer:", 1)[-1].strip()
            content = content[:content.find("Final Answer:")].strip()

        # Sidebar messages (Chain of Thought)
        if "Observation" in content:
            sidebar_messages.append(":orange[**Observation**] from :green[**Tool**] provided")
        elif "Thought:" in content or "Action:" in content or "PAUSE" in content:
            formatted_content = content.replace("Thought:", "\n:red[**Thought**]:") \
                                       .replace("Action:", "\n:blue[**Action**]:") \
                                       .replace("PAUSE", "\n:violet[**PAUSE**]")
            sidebar_messages.append(formatted_content)
        elif content:
            main_messages.append({"role": role, "content": content})

    #  Check if final answer is present and no main messages are present
    if final_answer and not main_messages:
        main_messages.append({"role": "assistant", "content": final_answer})

    return sidebar_messages, main_messages

# Display chat history
for message in st.session_state.chat_history:
    display_message(message["role"], message["content"])

# Main chat input
if user_input := st.chat_input("How can I help?"):
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    display_message("user", user_input)

    # Get response from FastAPI backend
    try:
        response = requests.post(FASTAPI_URL, json={"query": user_input})

        if response.status_code == 200:
            data = response.json()
            ai_response = data["response"]

            # Process messages into sidebar and main chat
            sidebar_messages, main_messages = process_messages(ai_response)

            # Display sidebar messages
            with st.sidebar:
                for sidebar_msg in sidebar_messages:
                    st.markdown(sidebar_msg)

            # Display main chat messages
            for msg in main_messages:
                st.session_state.chat_history.append(msg)
                display_message(msg["role"], msg["content"])

        else:
            st.error(f"Error: {response.status_code}, {response.json().get('detail', 'Unknown error')}")

    except Exception as e:
        st.error(f"An error occurred: {e}")






