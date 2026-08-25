from typing import Type, TypeVar
from pydantic import BaseModel
from openai import OpenAI
from .base import LLMProvider

T = TypeVar('T', bound=BaseModel)

class OpenAIAdapter(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-2024-08-06"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_structured(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        response_model: Type[T]
    ) -> T:
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=response_model,
        )
        return completion.choices[0].message.parsed
