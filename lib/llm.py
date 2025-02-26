from abc import ABC, abstractmethod
import chevron
from lib.logging import log_debug
from lib.config import configure
from icecream import ic
from pathlib import Path
from lib.image_utils import encode_image_openai_format

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
    def __init__(self, api_key, model: str = None):
        self.api_key = api_key
        self.model = model if model else "gpt-4o-mini"
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)

    def complete_user_prompt(self, system_prompt: str, user_prompt: str, image_paths=None) -> str:
        """
        Calls the OpenAI Chat Completions API.
        
        Parameters:
            system_prompt (str): The system prompt.
            user_prompt (str): The user prompt text.
            image_paths (str or list, optional): Path or list of paths to images. Each image is encoded
                for the OpenAI API.
                
        Returns:
            str: The response text.
        """
        # Create the user prompt message parts starting with text.
        user_content = [{"type": "text", "text": user_prompt}]
        
        # If image_paths are provided, encode and append them.

        if image_paths:
            # Should never happen, but ensure image_paths is a list.
            if not isinstance(image_paths, list):
                image_paths = [image_paths]
            for image_path in image_paths:
                path_obj = Path(image_path) if isinstance(image_path, str) else image_path
                if path_obj.exists():
                    encoded = encode_image_openai_format(path_obj)
                    user_content.append({
                        "type": "image_url",
                        "image_url": {"url": encoded}
                    })
                else:
                    # Optionally, log the missing file or handle the error.
                    user_content.append({
                        "type": "text",
                        "text": f"[Image not found: {image_path}]"
                    })
       
        # Prepare system prompt as a single text element.
        system_content = [{"type": "text", "text": system_prompt}]
        messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ]
        ic(messages)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ],
            )
            ic(response.choices[0].message.content.strip())

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
