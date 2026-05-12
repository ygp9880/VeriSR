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
    api_key=os.getenv("openai_key"),
    max_retries=5,
    timeout=180.0,
)

_anthropic_kwargs = {"api_key": os.getenv("anthropic_key") or os.getenv("openai_key")}
if os.getenv("anthropic_base_url"):
    _anthropic_kwargs["base_url"] = os.getenv("anthropic_base_url")
anthropic_client = Anthropic(**_anthropic_kwargs)

_genai_kwargs = {"api_key": os.getenv("google_key") or os.getenv("openai_key"), "vertexai": True}
if os.getenv("google_base_url"):
    _genai_kwargs["http_options"] = {"base_url": os.getenv("google_base_url")}
genai_client = genai.Client(**_genai_kwargs)

def get_client():
    return _client

def get_claude_client():
    return anthropic_client;

def get_genai_client():
    return genai_client;

