import yaml
import json

# Load the configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

def configure(parameter_name):
    # Check if parameter name contains a dot
    if '.' in parameter_name:
        # Split the parameter name by dot
        parameter_name_parts = parameter_name.split('.')
        # Initialize the parameter value
        parameter_value = config
        # Iterate over the parameter name parts
        for part in parameter_name_parts:
            # Get the value of the parameter
            parameter_value = parameter_value.get(part)
    else:
        # Get the value of the parameter 
        parameter_value = config.get(parameter_name)

    if parameter_value is None:
        print(f"Parameter {parameter_name} not found in the configuration")

    return parameter_value

def get_conversation(user_id, conversation_id):
    conversations_path = configure("data.conversations_path")
    # Load the configuration
    with open(f'{conversations_path}/{user_id}_{conversation_id}.json', 'r', encoding="utf-8") as f:
        conversation = json.load(f)
    return conversation

def save_conversation(conversation):
    conversations_path = configure("data.conversations_path")
    # Save the conversation
    with open(f'{conversations_path}/{conversation.get("user_id")}_{conversation.get("conversation_id")}.json', 'w', encoding="utf-8") as f:
        json.dump(conversation, f, ensure_ascii=False, indent=4)

def get_assistant(assistant_id):
    assistants_path = configure("data.assistants_path")
    # Load the configuration
    with open(f'{assistants_path}/{assistant_id}.yaml', 'r') as f:
        assistant_config = yaml.safe_load(f)
    return assistant_config

def get_agent(agent_id):
    agents_path = configure("data.agents_path")
    # Load the configuration
    with open(f'{agents_path}/{agent_id}.yaml', 'r') as f:
        agent_config = yaml.safe_load(f)
    return agent_config

def get_user(user_id):
    users_path = configure("data.users_path")
    # Load the configuration
    with open(f'{users_path}/{user_id}.json', 'r') as f:
        user = json.load(f)
    return user