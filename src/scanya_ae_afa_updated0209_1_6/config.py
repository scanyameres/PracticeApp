import os
from openai import OpenAI
from dotenv import load_dotenv

def get_client(API_provider) -> OpenAI:
    """
    Returns an OpenAI client instance.
    """
    load_dotenv()  # Load environment variables from .env file if present
    if API_provider == "OpenRouter":
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"]
        )

        # List available models for the specified API provider
        # for m in sorted(client.models.list(), key=lambda m: m.id):
        #    print(m.id)

    elif API_provider == "OpenAI":
        client = OpenAI(
            base_url="https://api.openai.com/v1",
            api_key=os.environ["OPENAI_API_KEY"]
        )

        # List available models for the specified API provider
        for m in sorted(client.models.list(), key=lambda m: m.id):
            print(m.id)
    else:
        raise ValueError(f"Unsupported API provider: {API_provider}")

    return client