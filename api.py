import os
import json
from lib.assistant import Assistant
from lib.user import User
from lib.logging import reset_log, log_info, log_error
from lib.config import configure

ASSISTANTS_PATH = configure("data.assistants_path")
CONVERSATIONS_PATH = configure("data.conversations_path")
PROMPT_TEMPLATES_PATH = configure("data.prompt_templates_path")
USERS_PATH = configure("data.users_path")

def init_user(conversation):
    user_id = conversation.get("user_id")
    if os.path.exists(f"{USERS_PATH}/{user_id}.json"):
        with open(f"{USERS_PATH}/{user_id}.json", "r", encoding="utf-8") as file:
            user = json.load(file)
            return User(user)
    else:
        log_error(f"User >{user_id}< not found")
        return None

def init_assistant(conversation, user):
    assistant_id = conversation.get("assistant_id")
    if os.path.exists(f"{ASSISTANTS_PATH}/{assistant_id}.json"):
        with open(f"{ASSISTANTS_PATH}/{assistant_id}.json", "r", encoding="utf-8") as file:
            assistant = json.load(file)
            return Assistant(assistant, user)
    else:
        log_error(f"Assistant >{assistant_id}< not found")
        return None
    
def get_conversation(conversation_id):
    if os.path.exists(f"{CONVERSATIONS_PATH}/{conversation_id}.json"):
        with open(f"{CONVERSATIONS_PATH}/{conversation_id}.json", "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        log_error(f"Conversation >{conversation_id}< not found")
        return None

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
                    conversations.append(conversation)
    return conversations

def save_conversation(conversation_id, conversation):
    with open(f"{CONVERSATIONS_PATH}/{conversation_id}.json", "w", encoding="utf-8") as file:
        json.dump(conversation, file, indent=4, ensure_ascii=False)

def reset_conversation(conversation_id, resetlog=True):
    conversation = get_conversation(conversation_id)
    conversation["lines"] = []
    save_conversation(conversation_id, conversation)

    if resetlog:
        reset_log()
    
def chat(conversation_id, user_message):

    log_info(f"Conversation {conversation_id}, new message: {user_message}")

    # Read the content from the conversations.json file
    conversation = get_conversation(conversation_id)

    # Add the user's message to the conversation
    user_message = {
        "role": "user",
        "content": user_message }
    
    conversation["lines"].append(user_message)
    
    # Get the user profile for this converstion
    user = init_user(conversation)

    # Initialize the assistant for this conversation
    assistant = init_assistant(conversation, user)

    # Pass the conversation to the assistant
    response = assistant.respond(conversation.get("lines"))

    #print(response)

    # Add the response to the conversation
    response_message = {
        "role": "assistant",
        "content": response }
    conversation["lines"].append(response_message)

    # Save the conversation back to the conversations.json file
    save_conversation(conversation_id, conversation)

    return response_message
