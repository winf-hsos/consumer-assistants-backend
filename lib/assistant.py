from lib.agent import Agent
from lib.config import get_assistant

class Assistant:
    def __init__(self, assistant_id):
        self.assistant_id = assistant_id
        self._setup()
        
    def _setup(self):
        assistant = get_assistant(self.assistant_id)
        self.assistant_description = assistant.get("assistant_description")

        # Assistant must have exactly one agent
        self._create_agent(assistant.get("agent_id"))

    def _create_agent(self, agent_id):
        self.agent = Agent(agent_id)

    def respond(self, input, user):
        answer = self.agent.respond(input, user)
        print(f"Answer: {answer}")
        return answer
        