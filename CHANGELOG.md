# Changelog

## 29.01.2024 - Philipp
- TODO 5 - llm factory added (currently only OpenAI)
- TODO 7 - added translation on conversation level (conversation.py)
- TODO 2 - Added step_strategy to agent level. Enum= ["sequential", "parallel"]. Sequential = last msg, Parallel = addition step -> new TODO
- Added Step Class "FunctionCallStep(BaseStep)" and "QuerySQLStep(FunctionCallStep)"
- Added file step_function_interface.py as a wrapper for all functions that will be executed in a step
- enhanced product_agent.yaml -> still clueless how to implement it in step logic

## 12.02.2024
- Implemented Product Agent. First end-to-end version now available
- Added SQL Step
- Added multiple prompt templates
- renamed mysql.py to sql.py to avoid module errors (original module is called mysql)