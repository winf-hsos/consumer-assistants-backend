from abc import ABC, abstractmethod
from lib.llm import OpenAILLM
from lib.config import configure
import chevron

def create_step(step_definition):
    """Factory function to create a step instance based on the step definition."""
    step_type = step_definition.get("type")
    if step_type == "decision_prompt":
        return DecisionPromptStep(step_definition)
    elif step_type == "list_from_prompt":
        return ListFromPromptStep(step_definition)
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
    def run(self, context):
        """Run the step's logic."""
        pass

    def evaluate_condition(self, context):
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

    def resolve_inputs(self, input_variables, context):
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

    def store_outputs(self, output_variables, outputs, context):
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
    def run_prompt(self, system_prompt_id, user_prompt_id, inputs, context):
        """Execute prompt using the external LLM class."""

        # Get the prompt templates based on the ids
        system_prompt = self.get_prompt_template(system_prompt_id, "system")
        user_prompt = self.get_prompt_template(user_prompt_id, "user")

        # Resolve placeholders in the prompts
        resolved_system_prompt = chevron.render(system_prompt, inputs)
        resolved_user_prompt = chevron.render(user_prompt, inputs)

        context.set_step_prompt(self.step_name, "system", resolved_system_prompt)
        context.set_step_prompt(self.step_name, "user", resolved_user_prompt)

        # Execute the prompt using the LLM class
        # TODO: Move the api_key to the LLM class
        api_key = configure("llm.openai_api_key")
        llm = OpenAILLM(api_key=api_key)
        llm_output = llm.complete_user_prompt(resolved_system_prompt, resolved_user_prompt)
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
        
        # Run the prompt logic
        outputs = self.run_prompt(
            system_prompt_id=prompt_templates.get("system", ""),
            user_prompt_id=prompt_templates.get("user", ""),
            inputs=inputs,
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
        outputs["list_items"] = ["expert_1", "expert_2", "expert_3"]  # Placeholder example

        # Store outputs back to execution context
        self.store_outputs(self.step_definition.get("output_variables", []), outputs, context)
