from datetime import datetime
import json

class ExecutionContext:
    """Central object holding all runtime data, logs, and metadata."""
    def __init__(self, agent, input, user):
        self.agent = agent
        self.user = user
       
        self.context = {}  # Holds variables grouped by step
        self.context["global"] = {
            "user": user.to_json(),
            "input": input
        }

        self.logs = []
        self.timestamp = datetime.now().isoformat()

    def retrieve_value(self, source):
        # Split source by dots
        source_parts = source.split(".")
        scope = source_parts[0]
        key = source_parts[1]
        if scope == "global":
            return self.context.get("global", {}).get(key, None)
        else:
            return self.get_step_output(scope, key)

    def set_step_output(self, step_name, key, value):
        """Set specific variable in a step's output."""
        if step_name not in self.context:
            self.context[step_name] = {}
        if "outputs" not in self.context[step_name]:
            self.context[step_name]["outputs"] = {}
        self.context[step_name]["outputs"][key] = value
        self.log(f"Set step '{step_name}' output: {key} = {value}")

    def set_step_input(self, step_name, key, value):
        """Set specific variable in a step's input."""
        if step_name not in self.context:
            self.context[step_name] = {}
        if "inputs" not in self.context[step_name]:
            self.context[step_name]["inputs"] = {}
        self.context[step_name]["inputs"][key] = value
        self.log(f"Set step '{step_name}' input: {key} = {value}")

    def set_step_prompt(self, step_name, prompt_type, prompt):
        if step_name not in self.context:
            self.context[step_name] = {}
        if "prompts" not in self.context[step_name]:
            self.context[step_name]["prompts"] = {}
        self.context[step_name]["prompts"][prompt_type] = prompt   

    def get_step_output(self, step_name, key):
        """Retrieve specific variable from a step's output."""
        return self.context.get(step_name, {}).get("outputs", {}).get(key, None)
    
    def get_step_input(self, step_name, key):
        """Retrieve specific variable from a step's input."""
        return self.context.get(step_name, {}).get("inputs", {}).get(key, None)

    def get_final_response(self):
        """Retrieve the final response from the execution context."""

        # TODO: Check if this logic makes sense. Currently, the last output from the last step is returned.
        # This might need to be adjusted based on the actual implementation.

        # Get the last step
        last_step = list(self.context.keys())[-1]

        # From the last step, get the last output key
        last_steps_outputs = self.context[last_step]["outputs"]
        last_output = list(last_steps_outputs.keys())[-1]
        return last_steps_outputs[last_output]

    def log(self, message, level="INFO"):
        """Log execution details."""
        self.logs.append({"timestamp": datetime.now().isoformat(), "level": level, "message": message})
        #print(f"[{level}] {message}")

    def save_to_file(self, filename):
        """Save the context and logs to a file."""
        with open(filename, "w", encoding="utf-8") as file:
            file.write(json.dumps(
                {
                    "agent_id": self.agent.agent_id,
                    "timestamp": self.timestamp,
                    "context": self.context,
                    "logs": self.logs
                },
                ensure_ascii=False,
                indent=4
            ))