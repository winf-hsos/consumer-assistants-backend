# TODOs

- [ ] Add timestamp to messages in conversation history (data/conversations/*.json)
- [ ] Determine the final response in ExecutionContext.get_final_response() is sensible way. Currently, the last step's last output is returned.
- [ ] Adjust Flask webserver (server.py)
- [ ] Fix logging; one way is in the ExecutionContext, another currently through a log_*() function in lib.logging.py. Not sure if this should be harmonized? Maybe both are needed