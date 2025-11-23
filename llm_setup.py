import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def get_llm(model_type="fast"):
    """
    Returns the LLM instance.
    'fast' = Groq Llama 3 70B (Great for loops/retries)
    'smart' = Gemini 1.5 Flash/Pro (Great for complex context)
    """
    if model_type == "fast":
        return ChatGroq(
            temperature=0, 
            model_name="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY")
        )
    elif model_type == "smart":
        return ChatGoogleGenerativeAI(
            temperature=0,
            model="gemini-1.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    else:
        raise ValueError("Unknown model type")