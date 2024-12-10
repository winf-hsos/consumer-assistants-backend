from lib.agent import PrincipalAgent
from lib.llm import translate
from lib.logging import log_debug

class Assistant:
    def __init__(self, assistant, user):
        self.assistant = assistant
        self.user = user
        self.principal_agent = self._create_principal_agent(assistant.get("principal_agent"))

    def _create_principal_agent(self, principal_agent):
        return PrincipalAgent(principal_agent)


    def respond(self, lines):
        answer = self.principal_agent.respond(lines)

        if self.user.language == "en":
            return answer
        else:
            return translate(answer, self.user.language)
