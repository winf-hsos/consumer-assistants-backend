import yaml

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