import streamlit as st
import os
import hashlib
from api import chat, get_conversation, reset_conversation, list_user_ids, list_conversations_for_user
from pathlib import Path
from typing import List

# Ensure the image directory exists
MAIN_DIR = Path(__file__).resolve().parent.parent
IMAGE_DIR = MAIN_DIR / "data/image"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

def get_file_hash(file) -> str:
    """Generate a SHA-256 hash for a file."""
    hasher = hashlib.sha256()
    hasher.update(file.getbuffer())
    return hasher.hexdigest()

st.title("Virtual Consumer Assistant")

user_ids = list_user_ids()
user_id = st.selectbox("Select user", user_ids)

# List conversations for the user
conversations = list_conversations_for_user(user_id)
# Dropdown to select conversation
conversation_id = st.selectbox("Select conversation", conversations)

conversation = get_conversation(user_id, conversation_id)

# Show the conversation as chat messages
if conversation_id:
    for message in conversation.lines:
        from icecream import ic
        ic(message)
        with st.chat_message(message["role"]):
            st.markdown(message["message"])
            # Display images if present in the message
            if "image_paths" in message and message["image_paths"]:
                for img in message["image_paths"]:
                    if img is not None:
                        st.image(img, caption="Uploaded Image", use_container_width=True)
    
    # Add button to reset conversation
    if st.button("Reset conversation"):
        reset_conversation(user_id, conversation_id)
        st.rerun()
    
    prompt = st.chat_input("What is up?")
    
    # Multiple image uploads
    uploaded_images = st.file_uploader("Upload images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    image_paths: List[str] = []
    
    if uploaded_images:
        for uploaded_image in uploaded_images:
            # Generate a unique filename based on hash
            image_hash = get_file_hash(uploaded_image)
            image_path = IMAGE_DIR / f"{image_hash}.jpg"
            
            # Save only if the file does not already exist
            if not image_path.exists():
                with open(image_path, "wb") as f:
                    f.write(uploaded_image.getbuffer())
            
            image_paths.append(str(image_path))
            st.image(image_path, caption="Uploaded Image", use_container_width=True)
    
    if prompt:
        with st.chat_message("user"):

            st.markdown(prompt)
            for img_path in image_paths:
                st.image(img_path, caption="Uploaded Image", use_container_width=True)
        
        with st.spinner("Thinking..."):
            chat(user_id, conversation_id, prompt, image_paths=image_paths)
            st.rerun()
