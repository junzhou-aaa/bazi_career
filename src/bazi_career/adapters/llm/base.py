from typing import Protocol, Type, TypeVar, Any
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class LLMProvider(Protocol):
    def generate_structured(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        response_model: Type[T]
    ) -> T:
        """Generate a structured response matching the given Pydantic model."""
        ...
