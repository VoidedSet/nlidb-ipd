# llm_setup.py
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def get_llm(model_type="fast"):
    """
    Returns the LLM instance.
    """
    if model_type == "fast":
        return ChatGoogleGenerativeAI(
            temperature=0,
            model="gemini-2.0-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            convert_system_message_to_human=True 
        )
    elif model_type == "groq":
        return ChatGroq(
            temperature=0, 
            model_name="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY")
        )
    else:
        raise ValueError("Unknown model type")