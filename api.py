import os
import json
from lib.assistant import Assistant
from lib.conversation import Conversation
from lib.user import User
from lib.logging import log_info
from lib.config import configure

ASSISTANTS_PATH = configure("data.assistants_path")
CONVERSATIONS_PATH = configure("data.conversations_path")
USER_PROMPT_TEMPLATES_PATH = configure("data.user_prompt_templates_path")
USERS_PATH = configure("data.users_path")

def get_user(user_id):
    user = User(user_id)
    return user

def get_assistant(assistant_id):
    assistant = Assistant(assistant_id)
    return assistant
    
def get_conversation(user_id, conversation_id):
    conversation = Conversation(user_id, conversation_id)
    return conversation

def list_user_ids():
    user_ids = []
    for file in os.listdir(USERS_PATH):
        if file.endswith(".json"):
            user_ids.append(file.replace(".json", ""))
    return user_ids

def list_conversations_for_user(user_id):
    conversations = []
    for file in os.listdir(CONVERSATIONS_PATH):
        if file.endswith(".json"):
            with open(f"{CONVERSATIONS_PATH}/{file}", "r", encoding="utf-8") as file:
                conversation = json.load(file)
                if conversation.get("user_id") == user_id:
                    conversations.append(conversation.get("conversation_id"))
    return conversations

def reset_conversation(user_id, conversation_id):
    conversation = get_conversation(user_id, conversation_id)
    conversation.reset()
    
def chat(user_id, conversation_id, user_message):

    log_info(f"User {user_id} continues conversation {conversation_id} with new message: >{user_message}<")

    # Read the content from the conversations.json file
    conversation = get_conversation(user_id, conversation_id)
    response = conversation.continue_conversation(user_message)

    return response.get("message")
