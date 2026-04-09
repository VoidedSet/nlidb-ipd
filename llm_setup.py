# llm_setup.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm(model_type="fast"):
    """
    Returns the LLM instance connected to Featherless AI.
    """
    # Featherless uses an OpenAI-compatible endpoint
    featherless_base_url = "https://api.featherless.ai/v1"
    api_key = os.getenv("FEATHERLESS_API_KEY")

    if not api_key:
        raise ValueError("FEATHERLESS_API_KEY is missing from the environment variables.")

    if model_type == "fast":
        return ChatOpenAI(
            temperature=0, 
            # Replace with the exact DeepSeek model ID available on your Featherless plan
            model="deepseek-ai/DeepSeek-V3-0324", 
            api_key=api_key,
            base_url=featherless_base_url
        )
    elif model_type == "groq" or model_type == "smart":
        return ChatOpenAI(
            temperature=0, 
            # You can use a heavier model here for the EDA agent
            model="deepseek-ai/DeepSeek-Coder-V2-Instruct", 
            api_key=api_key,
            base_url=featherless_base_url
        )
    else:
        raise ValueError("Unknown model type")