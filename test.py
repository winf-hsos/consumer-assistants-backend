# from api import chat, get_conversation, get_user, reset_conversation, list_user_ids, list_conversations_for_user

# conversation_id = "001"
# user_id = "nmeseth"

# def test_chat():
#     reset_conversation(user_id, conversation_id)
#     user_message = "Hello!"
#     response = chat(user_id, conversation_id, user_message)
#     print(response)


# user_ids = list_user_ids()
# print(user_ids)

# conversations = list_conversations_for_user(user_id)
# print(conversations)

# user = get_user(user_id)
# print(user.language)

# #test_chat()

from connections.sql import execute_select_query
query = "SELECT * FROM product WHERE identifier LIKE '%brötchen%' OR name LIKE '%brötchen%' OR description LIKE '%brötchen%' OR categories LIKE '%BREAD_BUNS%'"
rows = execute_select_query(query)
print(rows)