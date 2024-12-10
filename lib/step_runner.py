class StepRunner:
    def __init__(self):
        self.results = []
        pass

    def get_last_result(self):
        return self.results[-1] if len(self.results) > 0 else None
    
    def run_prompt(self, prompt_template, context):
        input = self.get_last_result()

        # Get prompt template

        # Render the prompt template

        # Execute the prompt

        self.results.append({})
        return self
    
    def run_sql_query(self, sql_query, context):
        input = self.get_last_result()

        self.results.append({})

        return self
    
    def run_rag_retrevial(self, rag_model, context):
        input = self.get_last_result()
        return self