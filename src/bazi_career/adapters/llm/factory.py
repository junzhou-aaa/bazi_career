from .base import LLMProvider
from .openai_adapter import OpenAIAdapter
from ...db import get_config

def get_llm_provider() -> LLMProvider:
    provider_name = get_config("llm_provider") or "openai"
    
    if provider_name == "openai":
        api_key = get_config("openai_api_key")
        if not api_key:
            raise ValueError("OpenAI API key is not configured. Run 'bazi-career configure' to set it up.")
        return OpenAIAdapter(api_key=api_key)
    else:
        raise NotImplementedError(f"Provider {provider_name} is not implemented.")
