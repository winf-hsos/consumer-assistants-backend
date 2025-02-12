from connections.sql import execute_select_query
from icecream import ic
def execute_query_select(query):
    '''Execute a select query and return the rows'''
    # TODO: add logging and error handling 
    rows = execute_select_query(query)
    if not rows:
        print(f"Error executing query: {query}")
        return None
    return rows