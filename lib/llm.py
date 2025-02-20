from abc import ABC, abstractmethod
import chevron
from lib.logging import log_debug
from lib.config import configure
from icecream import ic
USER_PROMPT_TEMPLATES_PATH = configure("data.user_prompt_templates_path")


def get_llm(provider=None, model=None):
    
    
    if not provider:
        provider = configure("llm.provider")
    if not model:
        model = configure("llm.model")

    if provider == "openai":
        api_key = configure("llm.api_key")
        llm = OpenAILLM(api_key, model)
    else:
        llm = None
        raise Exception(f"LLM provider >{provider}< not supported")
    return llm

class LLM(ABC):
    """
    Abstract base class for all LLM implementations.
    Defines the method for completing user prompts.
    """
    @abstractmethod
    def complete_user_prompt(self, system_prompt: str, user_prompt: str) -> str:
        """Takes system and user prompts and returns the completion text."""
        pass
    @abstractmethod
    def translate(self, text, target_language=None):
        pass

class OpenAILLM(LLM):
    """
    Concrete implementation of LLM using OpenAI's GPT-4o API.
    """
    def __init__(self, api_key, model:str=None):
        self.api_key = api_key
        self.model = model if model else "gpt-4o-mini"
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)

    def complete_user_prompt(self, system_prompt: str, user_prompt: str) -> str:
        """Simulates OpenAI GPT-4o API call and returns the response text."""

        try:
            response = self.client.chat.completions.create(
                model= self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {e}"

    def translate(self, text, target_language=None):
        if not target_language:
            target_language = "german"
        
        if target_language in["en", "english", "englisch"]:
            return text
        instructions = self._get_prompt_template("llm_translate_prompt")
        instructions = chevron.render(instructions, { "text": text, "target_language": target_language })
        
        log_debug("Starting translation",  instructions)
        messages = [ { "role": "user", "content": instructions } ]
        completion = self.client.chat.completions.create(model=self.model, messages=messages)
        log_debug("Completed translation",  completion.choices[0].message.content)
        
        return completion.choices[0].message.content

    def _get_prompt_template(self, prompt_id):
            with open(f"{USER_PROMPT_TEMPLATES_PATH}/{prompt_id}.mustache", "r", encoding="utf-8") as file:
                return file.read()
