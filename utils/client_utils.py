# openai_client.py
from dotenv import load_dotenv
import os
from openai import OpenAI
from anthropic import Anthropic
from google import genai
from google.genai import types

load_dotenv()

_client = OpenAI(
    base_url=os.getenv("openai_base_url"),
    api_key=os.getenv("openai_key")
)

anthropic_client = Anthropic(base_url='https://api.openai-proxy.org/anthropic',api_key=os.getenv("openai_key"))

genai_client = genai.Client(api_key=os.getenv("openai_key"), vertexai=True, http_options={"base_url": "https://api.openai-proxy.org/google"},)

def get_client():
    return _client

def get_claude_client():
    return anthropic_client;

def get_genai_client():
    return genai_client;

