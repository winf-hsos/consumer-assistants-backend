from abc import ABC, abstractmethod
from lib.llm import get_llm
from lib.config import configure
from lib.steps.step_function_interface import execute_query_select

from typing import TYPE_CHECKING
print("TYPE_CHECKING", TYPE_CHECKING)
if TYPE_CHECKING:
    from lib.steps.execution_context import ExecutionContext

import chevron
from datetime import datetime
from icecream import ic
def create_step(step_definition):
    """Factory function to create a step instance based on the step definition.
    Args:
        step_definition (dict): The step definition from the YAML file.
        agent (Agent): The agent instance to which the step belongs.
    """
    step_type = step_definition.get("type")
    if step_type == "decision_prompt":
        return DecisionPromptStep(step_definition)
    elif step_type == "list_from_prompt":
        return ListFromPromptStep(step_definition)
    elif step_type == "prompt":
        return PromptStep(step_definition)
    elif step_type == "string_from_prompt":
        return StringFromPromptStep(step_definition)
    elif step_type == "query_sql":
        return QuerySQLStep(step_definition)
    elif step_type == "run_expert":
        return RunExpertStep(step_definition)
    elif step_type == "summarize_expert_responses":
        return SummarizeExpertReponsesStep(step_definition)
    else:
        raise ValueError(f"Unknown step type: {step_type}")

class BaseStep(ABC):
    """
    Abstract base class for all steps.
    Defines the common interface and functionality for steps.
    """
    def __init__(self, step_definition):
        self.step_definition = step_definition
        self.step_name = step_definition.get("name")

    @abstractmethod
    def run(self, context:"ExecutionContext"):
        """Run the step's logic."""
        pass

    def evaluate_condition(self, context:"ExecutionContext"):
        """Evaluate the 'if' condition of a step."""
        condition = self.step_definition.get("if", None)
        if not condition:
            return True

        context.log(f"Evaluating condition: {condition}", level="DEBUG")

        # Split condition by "=" to separate variable and value
        parts = condition.split("=")
        if len(parts) != 2:
            context.log(f"Invalid condition: {condition}", level="ERROR")
            return False
        
        variable_name = parts[0].strip()
        expected_value = parts[1].strip()

        # Retrieve the actual value from the context
        actual_value = context.retrieve_value(variable_name)

        # Compare the actual value with the expected value
        if actual_value is None:
            context.log(f"Failed to retrieve value for variable: {variable_name}", level="ERROR")
            return False
        elif actual_value != expected_value:
            context.log(f"Condition not met: {actual_value} != {expected_value}", level="DEBUG")
            return False
        else:
            context.log(f"Condition met: {actual_value} == {expected_value}", level="DEBUG")

        return True    

    def resolve_inputs(self, input_variables, context:"ExecutionContext"):
        """Resolve input variables using the execution context."""
        resolved_inputs = {}
        for var in input_variables:
            input_name = var["input_name"]
            source = var["source"]
            value = context.retrieve_value(source)
            resolved_inputs[input_name] = value
            if value is None:
                context.log(f"Failed to resolve input variable >{input_name}<: '{source}'", level="WARNING")
            else:
                context.log(f"Resolved input variable >{input_name}<: '{value}'", level="DEBUG")
        return resolved_inputs

    def store_outputs(self, output_variables, outputs, context:"ExecutionContext"):
        """Store step outputs into the execution context."""
        for output_var in output_variables:
            name = output_var["output_name"]
            source = output_var["source"]
            context.set_step_output(self.step_name, name, outputs.get(source))
            context.log(f"Stored output '{name}' with value: {outputs.get(source)}", level="DEBUG")



class PromptStep(BaseStep):
    """
    Base class for all prompt-based steps.
    Handles prompt resolution, execution, and output storage.
    """
    def find_image_paths(self, inputs):
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

    def get_messages_from_inputs(self, inputs):
        '''
        Extrahiert Benutzer (role) und Nachrichten (message) aus inputs.
        '''
        messages = []
        
        if 'chat_history' in inputs and isinstance(inputs['chat_history'], list):
            for entry in inputs['chat_history']:
                if isinstance(entry, dict) and 'message' in entry and 'role' in entry:
                    messages.append({
                        "role": entry["role"],
                        "message": entry["message"]
                    })

        return messages
    def remove_image_paths(self, inputs):
        """Remove all occurrences of 'image_paths' from the input dictionary."""
        if isinstance(inputs, dict):
            # Erstelle eine Liste der zu löschenden Schlüssel, um während der Iteration nichts zu entfernen
            keys_to_remove = [key for key in inputs if key == "image_paths"]
            
            # Entferne die Schlüssel nach der Iteration
            for key in keys_to_remove:
                del inputs[key]
            
            # Rekursiver Aufruf für alle verschachtelten Werte
            for key, value in inputs.items():
                self.remove_image_paths(value)
        
        elif isinstance(inputs, list):
            for item in inputs:
                self.remove_image_paths(item)
        
        return inputs




    def run_prompt(self, system_prompt_id, user_prompt_id, inputs, context:"ExecutionContext"):
        """Execute prompt using the external LLM class."""
        # Get the prompt templates based on the ids
        system_prompt = self.get_prompt_template(system_prompt_id, "system")
        user_prompt = self.get_prompt_template(user_prompt_id, "user")
        
        image_paths = context.get_image_paths()

        # NOTE: Aus irgendeinem Grund hat das LLM Probleme, wenn die Pfade in der Chat History sind.
        inputs = self.remove_image_paths(inputs)
        
        # Resolve placeholders in the prompts
        resolved_system_prompt = chevron.render(system_prompt, inputs)
        resolved_user_prompt = chevron.render(user_prompt, inputs)
      
        context.set_step_prompt(self.step_name, "system", resolved_system_prompt)
        context.set_step_prompt(self.step_name, "user", resolved_user_prompt)

        # Call the LLM to complete the user prompt     
        llm = get_llm()
        llm_output = llm.complete_user_prompt(
            system_prompt=resolved_system_prompt, 
            user_prompt=resolved_user_prompt,
            image_paths=image_paths
            )
   
    
        return {"completion": llm_output}
    
    def get_prompt_template(self, prompt_id, prompt_type):
        if prompt_type == "system":
            PATH = configure("data.system_prompt_templates_path")
        else:
            PATH = configure("data.user_prompt_templates_path")
      #  prompt_id = next((prompt.get("prompt_id") for prompt in self.agent.get("prompts") if prompt.get("prompt_type") == prompt_type), None)
        with open(f"{PATH}/{prompt_id}.mustache", "r", encoding="utf-8") as file:
            return file.read()

class DecisionPromptStep(PromptStep):
    """
    Executes a decision prompt step.
    Parses the completion into 'decision_code' and 'decision_text' based on YAML-defined options.
    """
    def run(self, context):
 
        inputs = self.resolve_inputs(self.step_definition.get("input_variables", []), context)


        if(self.evaluate_condition(context)):
            context.log(f"Running decision prompt with inputs: {inputs}", level="DEBUG")
        else:
            context.log(f"Skipping decision prompt due to unmet condition >{self.step_definition.get('if')}<", level="DEBUG")
            return
        
        prompt_templates = self.step_definition.get("prompt_templates", {})

        # TODO: Make more robust than assuming options are in the first output variable
        options = self.step_definition.get("output_variables", [])[0].get("options", [])
        
        #for debug only
        from copy import deepcopy
        inputs_copy = deepcopy(inputs)
        # Run the prompt logic
        outputs = self.run_prompt(
            system_prompt_id=prompt_templates.get("system", ""),
            user_prompt_id=prompt_templates.get("user", ""),
            inputs=inputs_copy,
            context=context
        )

        # Parse completion into decision_code and decision_text
        completion = outputs.get("completion", "")
        decision_code, decision_text = None, None
        context.log(f"Parsing completion: {completion} with options {options}", level="DEBUG")
        for option in options:
            if option in completion:
                decision_code = option
                decision_text = completion.split(option, 1)[-1].strip()
                break

        parsed_outputs = {
            "decision_code": decision_code or "UNKNOWN",
            "decision_text": decision_text or completion
        }

        context.log(f"{self.step_name}: Parsed outputs: {parsed_outputs}", level="DEBUG")

        # Store outputs back to execution context
        self.store_outputs(self.step_definition.get("output_variables", []), parsed_outputs, context=context)


class ListFromPromptStep(PromptStep):
    """
    Executes a step that generates a list from a prompt.
    """
    def run(self, context):
  
        inputs = self.resolve_inputs(self.step_definition.get("input_variables", []), context)

        if(self.evaluate_condition(context)):
            context.log(f"Running decision prompt with inputs: {inputs}", level="DEBUG")
        else:
            context.log(f"Skipping decision prompt due to unmet condition >{self.step_definition.get('if')}<", level="DEBUG")
            return
     
        prompt_templates = self.step_definition.get("prompt_templates", {})
        # Run the prompt logic
        outputs = self.run_prompt(
            system_prompt_id=prompt_templates.get("system", ""),
            user_prompt_id=prompt_templates.get("user", ""),
            inputs=inputs,
            context=context
        )
        
      
        # For this step, parse output into a list (simulate)
        items = outputs.get("completion", "").split("\n")
        outputs["list_items"] = items  # Placeholder example

        # Store outputs back to execution context
        self.store_outputs(self.step_definition.get("output_variables", []), outputs, context)

class StringFromPromptStep(PromptStep):
    """
    Executes a step that generates a string from a prompt.
    """
    def run(self, context):
        inputs = self.resolve_inputs(self.step_definition.get("input_variables", []), context)
   
        if(self.evaluate_condition(context)):
            context.log(f"Running decision prompt with inputs: {inputs}", level="DEBUG")
        else:
            context.log(f"Skipping decision prompt due to unmet condition >{self.step_definition.get('if')}<", level="DEBUG")
            return

        prompt_templates = self.step_definition.get("prompt_templates", {})

        # Run the prompt logic
        outputs = self.run_prompt(
            system_prompt_id=prompt_templates.get("system", ""),
            user_prompt_id=prompt_templates.get("user", ""),
            inputs=inputs,
            context=context
        )
     
        completion = outputs.get("completion")
        output = {"string" : str(completion)}  # Placeholder example
        
        

        # Store outputs back to execution context
        self.store_outputs(self.step_definition.get("output_variables", []), output, context)


class RunExpertStep(BaseStep):
    # self.agents sind bereits bekannt im ExecutionContext (context), dann agent.responsed(context) aufrufen 
    def _format_orchestrator_message_to_input(self, message):
        '''Format message from orchestrator to input for expert-agent'''
        #TODO: Check if role user or system
        return {"message": message, "role": "user", "timestamp": datetime.now().isoformat()}
    def run(self, context):
        inputs = self.resolve_inputs(self.step_definition.get("input_variables", []), context)
        if(self.evaluate_condition(context)):
            context.log(f"Running decision prompt with inputs: {inputs}", level="DEBUG")
        else:
            context.log(f"Skipping decision prompt due to unmet condition >{self.step_definition.get('if')}<", level="DEBUG")
            return
        expert_names = inputs.get("experts")
        orchestrator_message = inputs.get("message")
        input_message = self._format_orchestrator_message_to_input(orchestrator_message)
        if not isinstance(expert_names, list):
            # TODO: Errorhandling
            raise ValueError("Experts must be a list")
        responses = []

        for expert_name in expert_names:
            context.log(f"Running expert: {expert_name}", level="DEBUG")
            new_agent = context.agent.get_subagent_by_name(expert_name)
            # context is hand over if the agent is a subagent. So it has access to previous information
            response = new_agent.respond(input_message, context.user)
            responses.append(response)
        # Store outputs back to execution context
        responses = responses[0] # TODO: IMPLEMENT SUMMARIZATION LOGIC
        output = {"answers": responses}

        self.store_outputs(self.step_definition.get("output_variables", []), output, context)

class SummarizeExpertReponsesStep(PromptStep):
    def run(self, context):
        inputs = self.resolve_inputs(self.step_definition.get("input_variables", []), context)
        responses = inputs.get("responses")

        if not isinstance(responses, list):
            raise ValueError("Responses must be a list")
        if len(responses) == 0:
            raise ValueError("No responses to summarize")
        if len(responses) == 1:
            summary = responses[0]
        else:
            # TODO: Implement summarization logic
            context.log("Summarization logic not implemented yet", level="WARNING")
            summary = " ".join(responses)
        # Store outputs back to execution context
        self.store_outputs(self.step_definition.get("output_variables", []), {"summary": summary}, context)

class QuerySQLStep(BaseStep):

    def _eval_query(self, query:str):
        pass

    def run(self, context):
        inputs = self.resolve_inputs(self.step_definition.get("input_variables", []), context)

        if(self.evaluate_condition(context)):
            context.log(f"Running function call with inputs: {inputs}", level="DEBUG")
        else:
            context.log(f"Skipping function call due to unmet condition >{self.step_definition.get('if')}<", level="DEBUG")
            return
        
        rows = execute_query_select(inputs.get("sql_query"))
        output = {"query_results" : rows}

        self.store_outputs(self.step_definition.get("output_variables", []), output, context)