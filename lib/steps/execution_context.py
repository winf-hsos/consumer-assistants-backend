from datetime import datetime
import json
import os
from icecream import ic
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
        self.context["agents"] = {
            "introductions": self.agent.get_agents_introductions()
        }
        self.set_image_paths(self.extract_image_paths_from_inputs())

        self.logs = []
        
        self.timestamp = datetime.now().isoformat()

    def get_last_output(self)->str:
        """Retrieve the last output from the context."""
        last_step = list(self.context.keys())[-1]
        # From the last step, get the last output key
        last_steps_outputs = self.context[last_step]["outputs"]
        last_output = list(last_steps_outputs.keys())[-1]
 
        return last_steps_outputs[last_output]

    def retrieve_value(self, source):
        # Split source by dots
        source_parts = source.split(".")
        scope = source_parts[0]
        key = source_parts[1]
        if scope == "global":
            return self.context.get("global", {}).get(key, None)
        elif scope == "agents":
            return self.context.get("agents", {}).get(key, None)
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
    
    
    def extract_image_paths_from_inputs(self):
        """Retrieve image paths from the input."""
        inputs = self.get_input()
        if isinstance(inputs, dict):
            for key, value in inputs.items():
                if key == "image_paths":
                    return value  # Return the first occurrence of image_paths
                result = self.find_image_paths(value)  # Recursively check nested structures
                if result:
                    return result
        elif isinstance(inputs, list):
            for item in inputs:
                result = self.find_image_paths(item)
                if result:
                    return result
        return None  # Return None if no image_paths key is found
    
    def set_image_paths(self, image_paths):
        '''Set image paths in the global context'''
        if not image_paths:
            return
        self.context["global"]["image_paths"] = image_paths
    def get_image_paths(self):
        '''Retrieve image paths from the global context'''
        return self.context.get("global", {}).get("image_paths", None)
    def extract_image_paths_from_inputs(self, inputs=None):
        """Retrieve image paths from the input."""
        if not inputs:
            inputs = self.get_input()
        if isinstance(inputs, dict):
            for key, value in inputs.items():
                if key == "image_paths":
                    return value  # Return the first occurrence of image_paths
                result = self.extract_image_paths_from_inputs(value)  # Recursively check nested structures
                if result:
                    return result
        elif isinstance(inputs, list):
            for item in inputs:
                result = self.extract_image_paths_from_inputs(item)
                if result:
                    return result
        return None  # Return None if no image_paths key is found
    def get_step_output(self, step_name, key):
        """Retrieve specific variable from a step's output."""
        return self.context.get(step_name, {}).get("outputs", {}).get(key, None)
    
    def get_step_input(self, step_name, key):
        """Retrieve specific variable from a step's input."""
        return self.context.get(step_name, {}).get("inputs", {}).get(key, None)
    def get_input(self):
        return self.context.get("global", {}).get("input", None)

    def get_final_response(self):
        """Retrieve the final response from the execution context."""
        return self.get_last_output()


    def log(self, message, level="INFO"):
        """Log execution details."""
        self.logs.append({"timestamp": datetime.now().isoformat(), "level": level, "message": message})
        # print(f"[{level}] {message}")

    def save_to_file(self, filename):
        """Save the context and logs to a file."""

        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

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
    def __str__(self):
        """Returns a JSON string representation of the object for easier readability."""
        return json.dumps(
            {
                "agent_id": self.agent.agent_id,
                "timestamp": self.timestamp,
                "context": self.context,
                "logs": self.logs
            },
            ensure_ascii=False,
            indent=4
        )

    def __repr__(self):
        """Use the same representation as __str__ for debugging purposes."""
        return self.__str__()