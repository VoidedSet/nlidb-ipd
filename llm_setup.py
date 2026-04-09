import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

load_dotenv()

def get_llm(role="router"):
    if role == "planner":
        # DeepSeek on Featherless for 1-shot reasoning/planning
        return ChatOpenAI(
            model="deepseek-ai/DeepSeek-V3-0324", 
            api_key=os.getenv("FEATHERLESS_API_KEY"),
            base_url="https://api.featherless.ai/v1",
            temperature=0.2
        )
    elif role == "coder":
        # Qwen 3 32B on Groq for rapid, iterative code execution
        return ChatGroq(
            # model="qwen/qwen3-32b", # You can also swap this to "llama-3.3-70b-versatile"
            model="llama-3.3-70b-versatile", # You can also swap this to ""
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0
        )

        # return ChatOpenAI(
        #     model="Qwen/Qwen2.5-Coder-32B-Instruct", 
        #     api_key=os.getenv("FEATHERLESS_API_KEY"),
        #     base_url="https://api.featherless.ai/v1",
        #     temperature=0.49
        # )
    
    elif role == "router":
        return ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    else:
        raise ValueError("Unknown agent role")