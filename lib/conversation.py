from lib.config import get_conversation, save_conversation
from lib.assistant import Assistant
from lib.user import User

class Conversation:
    def __init__(self, user_id, conversation_id):
        self.conversation_id = conversation_id
        self.user_id = user_id
        self._setup()

    def _setup(self):
        conversation = get_conversation(self.user_id, self.conversation_id)

        # TODO: Check if user_id matches the given user_id

        # Load the user
        self.user = User(self.user_id)
       
        # Load the assistant
        self.assistant_id = conversation.get("assistant_id")
        self.assistant = Assistant(self.assistant_id)

        # Get the conversation lines
        self.lines = conversation.get("lines")

    def whos_turn(self):
        if len(self.lines) == 0:
            return "user"
        else:
            return "assistant" if self.lines[-1].get("role") == "user" else "user"

    def reset(self):
        self.lines = []
        save_conversation(self.to_json())

    def get_assistant(self):
        return self.assistant
    
    def get_user(self):
        return self.user
    
    def to_json(self):
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "assistant_id": self.assistant_id,
            "lines": self.lines
        }
    
    def continue_conversation(self, user_message = None):
        if user_message:
            message = { "role": "user", "message": user_message }
            self.lines.append(message)
    
        response = self.assistant.respond(self.lines, self.user)
        message = { "role": "assistant", "message": response }
        self.lines.append(message)

        save_conversation(self.to_json())
        return message

    
