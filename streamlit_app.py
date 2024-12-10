import streamlit as st
from api import chat, get_conversation, reset_conversation, list_user_ids, list_conversations_for_user

st.title("Virtual Consumer Assistant")

user_ids = list_user_ids()
user_id = st.selectbox("Select user", user_ids)

# List conversations for the user
conversations = list_conversations_for_user(user_id)
# Dropdown to select conversation
conversation_id = st.selectbox("Select conversation", [conversation["conversation_id"] for conversation in conversations])

conversation = get_conversation(conversation_id)

# Show the conversation as chat messages
if conversation_id:
    for message in conversation["lines"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Add button to reset conversation
    if st.button("Reset conversation"):
        reset_conversation(conversation_id)
        st.rerun()

    if prompt := st.chat_input("What is up?"):
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.spinner("Denke nach..."):
            chat(conversation_id, prompt)
            st.rerun()