import os
import chevron
from lib.logging import log_debug
from lib.config import configure
PROMPT_TEMPLATES_PATH = configure("data.prompt_templates_path")
os.environ["OPENAI_API_KEY"] = ( configure("openai.api_key") )
from openai import OpenAI
client = OpenAI()

def complete_user_prompt(prompt, model="gpt-4o-mini"):
     log_debug("Completing user prompt",  prompt)
     messages = [ { "role": "user", "content": prompt } ]
     completion = client.chat.completions.create(model=model, messages=messages)
     return completion.choices[0].message.content

def translate(text, target_language):

    instructions = _get_prompt_template("llm_translate_prompt")
    instructions = chevron.render(instructions, { "text": text, "target_language": target_language })
    
    log_debug("Starting translation",  instructions)
    messages = [ { "role": "user", "content": instructions } ]
    completion = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
    log_debug("Completed translation",  completion.choices[0].message.content)
    
    return completion.choices[0].message.content

def _get_prompt_template(prompt_id):
        with open(f"{PROMPT_TEMPLATES_PATH}/{prompt_id}.mustache", "r", encoding="utf-8") as file:
            return file.read()
