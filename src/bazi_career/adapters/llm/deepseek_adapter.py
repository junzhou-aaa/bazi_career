from typing import Type, TypeVar
from pydantic import BaseModel
from openai import OpenAI
from .base import LLMProvider
import json

T = TypeVar('T', bound=BaseModel)

class DeepSeekAdapter(LLMProvider):
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        # DeepSeek uses an OpenAI-compatible API format
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        self.model = model

    def generate_structured(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        response_model: Type[T]
    ) -> T:
        # For DeepSeek, we use json_object response format and inject the schema into the prompt.
        schema_json = response_model.model_json_schema()
        
        enhanced_system_prompt = (
            f"{system_prompt}\n\n"
            f"You MUST respond ONLY with valid JSON. "
            f"The JSON must strictly conform to the following schema:\n"
            f"{json.dumps(schema_json, indent=2)}"
        )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": enhanced_system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Received empty response from DeepSeek")
            
        return response_model.model_validate_json(content)
