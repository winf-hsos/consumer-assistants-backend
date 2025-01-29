from lib.logging import log_debug
from lib.config import configure, get_agent
from lib.steps.step import create_step
from lib.steps.execution_context import ExecutionContext

USER_PROMPT_TEMPLATES_PATH = configure("data.user_prompt_templates_path")

class Agent:
    def __init__(self, agent_id):
        log_debug(f"Creating agent >{agent_id}<")
        self.agent_id = agent_id
        self._setup()

    def _setup(self):
        agent = get_agent(self.agent_id)
        self.step_strategy = agent.get("step_strategy")
        self.introduction = agent.get("agent_introduction")

        # Create the agent's processing steps
        steps = agent.get("steps")
        self.steps = []
        for step in steps:
            self.steps.append(create_step(step))

        # Add expert agents to the agent
        self.agents = []
        self._create_agents(agent.get("agents"))
    
    def _create_agents(self, agents):
        if len(self.agents) == 0:
            return
        
        for agent_id in agents:
            self.agents.append(Agent(agent_id))

    def introduce(self):
        return self.introduction
    
    def get_agents_introductions(self):
        agents_introductions = []
        for agent in self.agents:
            agents_introductions.append(agent.introduce())
        
        # Concatenate all the introductions into a single string separated by new lines and enclosed in quotes
        agents_introductions = "\n\n".join([f'"{introduction}"' for introduction in agents_introductions])
        return agents_introductions

    def to_json(self):
        return {
            "agent_id": self.agent_id,
            "introduction": self.introduction,
            "steps": [step.to_json() for step in self.steps]
        }


    def respond(self, input, user):
        context = ExecutionContext(self, input, user)
        for step in self.steps:
            step.run(context)
        
        context.save_to_file(f"tmp/{self.agent_id}.json")

        # Determine the final response based on the execution context
        response = context.get_final_response(step_strategy=self.step_strategy)

        return response