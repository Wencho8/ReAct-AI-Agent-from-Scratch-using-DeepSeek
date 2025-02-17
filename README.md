# ReAct AI Agent from Scratch using DeepSeek 🐳

This repository contains a **ReAct (Reasoning + Acting) AI agent** built from scratch using **Python** and **DeepSeek**.


## 📌 Features
✅ **Reasoning Loop** built from scratch with prompt-based control  
✅ **Memory Management** using 🤗Transformers library to count tokens in formatted messages  
✅ **Tool integration** with a scalable tool environment. Not using function-calling API features  
✅ **Streamlit UI** to interact with the agent and display its responses and reasoning process  
✅ **FastAPI backend** for handling chat requests from Streamlit

<br>

## 🔧 How to Set Up  


1️⃣ **Clone the repository**  
```bash
git clone https://github.com/Wencho8/ReAct-AI-Agent-from-Scratch-using-DeepSeek.git
cd ReAct-AI-Agent-from-Scratch-using-DeepSeek
```
2️⃣ **Set up environment variables**  

Copy the example environment file and configure your API keys:  
```bash
cp .env.example .env
```
3️⃣ **Install dependencies**
```bash
pip install -r requirements.txt
```

<br>

## 🚀 How to Run

### 🖥️ Running from the Terminal
If you'd like to run the agent directly from the terminal without using the UI:
```bash
cd Agent
python agent.py
```
This will start the agent, allowing you to interact with it via the command line.


### 🌐 Using the UI

1️⃣ ***Start the FastAPI Backend***

```bash
cd Agent
python -m uvicorn app:app --reload
```

2️⃣ ***Start the Streamlit UI***

```bash
python -m streamlit run chat_ui.py
```





