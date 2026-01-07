import os
from abc import ABC, abstractmethod

# Try importing dependencies
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate_content(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate content from the LLM.
        
        Args:
            system_prompt: The system instruction/context.
            user_prompt: The user's input command.
            
        Returns:
            str: The generated text response.
        """
        pass


class GeminiProvider(LLMProvider):
    """Gemini implementation of LLMProvider."""
    
    def __init__(self, api_key: str, model_name: str = 'gemini-2.5-flash'):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-genai package is not installed.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_content(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
            config={
                'system_instruction': system_prompt
            }
        )
        return response.text


class OpenAIProvider(LLMProvider):
    """OpenAI implementation of LLMProvider."""
    
    def __init__(self, api_key: str, model_name: str = 'gpt-4o'):
        if not OPENAI_AVAILABLE:
             raise ImportError("openai package is not installed.")
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def generate_content(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content
