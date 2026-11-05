"""API client setup: one OpenAI SDK client, pointed at OpenRouter (used by the app) or OpenAI.

API keys come from the .env file in the project root (git-ignored; see .env.example).

Public function: get_client().
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

# Provider name -> (API base URL, environment variable holding its API key).
PROVIDERS = {
    "OpenRouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    "OpenAI": ("https://api.openai.com/v1", "OPENAI_API_KEY"),
}


def get_client(provider: str) -> OpenAI:
    """Return an OpenAI SDK client for `provider` ("OpenRouter" or "OpenAI").

    OpenRouter speaks the same API as OpenAI, so the same SDK works for both; only the base
    URL and the key differ.

    Raises:
        ValueError: for an unknown provider.
        KeyError: if the provider's API key is missing from .env / the environment.
    """
    if provider not in PROVIDERS:
        raise ValueError(f"Unsupported API provider: {provider}")
    load_dotenv()  # Read .env into the environment (does not override variables already set).
    base_url, key_variable = PROVIDERS[provider]
    return OpenAI(base_url=base_url, api_key=os.environ[key_variable])
