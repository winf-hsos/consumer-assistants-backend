# TODOs


- [x] 1. Add timestamp to messages in conversation history (data/conversations/*.json)
- [x] 2. Determine the final response in ExecutionContext.get_final_response() is sensible way. Currently, the last step's last output is returned.
- [ ] 3. Adjust Flask webserver (server.py)
- [ ] 4. Fix logging; one way is in the ExecutionContext, another currently through a log_*() function in lib.logging.py. Not sure if this should be 
harmonized? Maybe both are needed
- [x] 5. LLM Factory: get llm by name through a factory function
- [x] 6. Add translate as abstract function llm base
- [x] 7. Add translate execution to agent (?)
- [ ] ~~8. Add parallel logic for step strategy (follow up TODO 2). This can also be a step imo.~~
- [x] 9. Modify pricipal_agent_step 2: Add Inputs for mustache placeholer {expert_introduction}
- [ ] 10. Manage Expert Response if multiple Experts were requested.
- [ ] 11. Limit SQL Rows -> maybe add Loop here
- [ ] 12. Add User Information to prompt template, especically for product agent. -> Develop ideas and approaches
- [ ] 13. Check mysql datetime return: Error when save as json. Maybe parse dict to json string. 
- [ ] 14. Implement User Preference Agent
- [ ] 15. Add Image Support
- [ ] 16. Make openai api key general key for provider in config
- [ ] 17. Make sure SQL results are limited to a useful number of rows (see 11)
- [ ] 18. Return useful messages in case of errors