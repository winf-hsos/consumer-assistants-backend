from lib.llm import complete_user_prompt
from lib.logging import log, log_debug
from lib.config import configure
from connections.mysql import execute_select_query
import chevron

PROMPT_TEMPLATES_PATH = configure("data.prompt_templates_path")

class Agent:
    def __init__(self, agent):
        log_debug(f"Creating agent {agent.get('agent_id')}")
        self.agent = agent
        self.agent_id = agent.get("agent_id")
        self.expert_agents = []
        self._create_expert_agents(agent.get("expert_agents"))
    
    def _create_expert_agents(self, expert_agents):
        if expert_agents is None:
            return
        
        for agent in expert_agents:
            if agent.get("agent_type") == None:
                self.expert_agents.append(ExpertAgent(agent))
            elif agent.get("agent_type") == "database_agent":
                self.expert_agents.append(DatabaseAgent(agent))

    def get_agent_id(self):
        return self.agent_id

    def introduce(self):
        agent_introduction = self.agent.get("agent_introduction")
        import chevron
        return chevron.render(agent_introduction, self.agent)

    def get_prompt_template_instance(self, prompt_type):
        prompt_id = next((prompt.get("prompt_id") for prompt in self.agent.get("prompts") if prompt.get("prompt_type") == prompt_type), None)
        with open(f"{PROMPT_TEMPLATES_PATH}/{prompt_id}.mustache", "r", encoding="utf-8") as file:
            return file.read()

    def respond(self, lines):
        pass

class PrincipalAgent(Agent):
    def __init__(self, agent):
        super().__init__(agent)
        
    def _get_experts_introductions(self):
        experts_introductions = []
        for expert_agent in self.expert_agents:
            experts_introductions.append(expert_agent.introduce())
        
        # Concatenate all the introductions into a single string separated by new lines and enclosed in quotes
        experts_introductions = "\n\n".join([f'"{introduction}"' for introduction in experts_introductions])
        return experts_introductions
  
    def respond(self, lines):

        #### STEP 1: Summarize the user query ####
        # Get prompt for summarizing user query
        user_query_summary_prompt = self.get_prompt_template_instance("summarize_user_query")

        placeholder_values = {"chat_history": lines}

        user_query_summary_prompt = chevron.render(user_query_summary_prompt, placeholder_values)
        #print(user_query_summary_prompt)

        user_query = complete_user_prompt(user_query_summary_prompt)
        log_debug(f"summarized user query: {user_query}")

        # if starts with FOLLOWUP
        if user_query.startswith("FOLLOWUP"):
            user_query = user_query.split("FOLLOWUP:")[1]
            return user_query
        elif user_query.startswith("SMALLTALK"):
            user_query = user_query.split("SMALLTALK:")[1]
            return user_query
        else:
            user_query = user_query.split("SUMMARY:")[1]

        #### STEP 2: IDENTIFY THE EXPERT AGENTS ####

        # Get prompt for selecting expert agents
        user_select_experts_prompt = self.get_prompt_template_instance("select_experts")

        placeholder_values = {
            "experts_introductions": self._get_experts_introductions(),
            "user_query": user_query
        }

        user_select_experts_prompt = chevron.render(user_select_experts_prompt, placeholder_values)
        #print(user_select_experts_prompt)

        expert_selection = complete_user_prompt(user_select_experts_prompt)
        log_debug(f"selected experts: {expert_selection}")
        
        #### STEP 3: PASS QUERY TO EXPERT AGENTS ####

        # Split the expert selection into a list of expert agent names
        expert_agents = expert_selection.split(",")
        responses = []
        for expert in self.expert_agents:
            if expert.get_agent_id() in expert_agents:
                responses.append(expert.respond(user_query))

        # TODO: add validation
        #print(responses)

        #### STEP 4: AGGREGATE RESPONSES FROM EXPERTS ####

        #### STEP 5: RETURN RESPONSE TO ASSISTANT ####

        return responses[0]
    
class ExpertAgent(Agent):
    def __init__(self, expert_agent):
        super().__init__(expert_agent)

    def respond(self, query):
        answer_query_prompt_template = self.get_prompt_template_instance("answer_query")

        placeholder_values = {
            "user_query": query
        }

        answer_query_prompt_template = chevron.render(answer_query_prompt_template, placeholder_values)

        return complete_user_prompt(answer_query_prompt_template)
    
class DatabaseAgent(Agent):
    def __init__(self, agent):
        super().__init__(agent)
        
    def _clean_query(self, query, limt=20):
        # Remmove ```sql from the start and ``` from the end
        query = query.replace("```sql", "").replace("```", "")

        # Make sure there is a limit set at the end of the query
        query = query.strip().rstrip(";")
        query = query.strip() + f" LIMIT {limt};"

        return query
    
    def _execute_query(self, query):
        ... 

    def respond(self, query):
        
        #### STEP 1: GENERATE SQL QUERY ####
        generate_sql_query_prompt_template = self.get_prompt_template_instance("generate_sql_query")
        placeholder_values = { "user_query": query }
        generate_sql_query_prompt_template = chevron.render(generate_sql_query_prompt_template, placeholder_values)

        sql_query = complete_user_prompt(generate_sql_query_prompt_template, model="gpt-4o")
        sql_query = self._clean_query(sql_query)
        print(sql_query)

        #### STEP 2: EXECUTE SQL QUERY ####
        # Execute the query
        rows = execute_select_query(sql_query)
        
        # If no rows are returned, retry
        if len(rows) == 0:
            ...
        print(rows)