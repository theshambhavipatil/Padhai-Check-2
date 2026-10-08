from google import genai
from google.genai import types
from typing import Optional, Dict, Any
import os


class BaseAgent:
    _client: Optional[genai.Client] = None

    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt

    @property
    def client(self) -> genai.Client:
        if BaseAgent._client is None:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    "GEMINI_API_KEY environment variable is not set. Please add your Google AI API key from https://aistudio.google.com/app/apikey")
            BaseAgent._client = genai.Client(api_key=api_key)
        return BaseAgent._client

    def process(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        user_content = content
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            user_content = f"Context:\n{context_str}\n\nContent to process:\n{content}"

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(role="user", parts=[types.Part(text=user_content)])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=0.3,
                    max_output_tokens=4000
                ),
            )
            result = response.text
            return result if result else ""
        except Exception as e:
            raise Exception(f"Agent {self.name} failed: {str(e)}")
