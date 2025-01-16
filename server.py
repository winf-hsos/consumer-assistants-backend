from flask import Flask, request, jsonify
from api import chat as chat_api, list_conversations_for_user, reset_conversation as reset_conversation_api

app = Flask(__name__)

@app.route('/reset_conversation/<user_id>/<conversation_id>', methods=['POST'])
def reset_conversation(user_id, conversation_id):
    try:
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        if not conversation_id:
            return jsonify({"error": "Conversation ID is required"}), 400
        
        # Call the api module to reset the conversation
        reset_conversation_api(user_id, conversation_id)
        
        return jsonify({"message": "Conversation successfully reset"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/conversations/<user_id>', methods=['GET'])
def conversations(user_id):
    try:
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        # Call the api module to list the conversations for the user
        conversations = list_conversations_for_user(user_id)
        
        return jsonify({"conversations": conversations}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat/<conversation_id>', methods=['POST'])
def chat(user_id, conversation_id):
    try:
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        if not conversation_id:
            return jsonify({"error": "Conversation ID is required"}), 400

        # Parse the JSON payload
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Missing 'message' in request payload"}), 400
        
        user_message = data['message']
        
        # For demonstration purposes, echo back the message
        #response_message = f"You said: {user_message}"

        chat_response = chat_api(user_id, conversation_id, user_message.get("content"))
        
        return jsonify({"response": chat_response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
