# Consumer Assistant Backend

This repository contains the backend code for an LLM-based consumer assistant framework. The framework is developed in the course of the InVerBio research project, funded by the German Federal Ministry of Food and Agriculture (BMEL).

# Usage

# Clone the repository

Clone the repository using the following command:

```bash
git clone https://github.com/winf-hsos/consumer-assistant-backend.git
```

In a file explorer, navigate to the `consumer-assistant-backend` folder and rename the `config.yaml.rename` file to `config.yaml`.

## Installation

We recommend using a Python virtual environment to install the required packages. Create a new virtual environment using the following command:

```bash
python -m venv .env
```

Activate the virtual environment using the following command:

```bash
source .env/bin/activate
```

or on Windows:

```bash
.env\Scripts\activate
```

Install the required packages using `pip`:

```bash
pip install -r requirements.txt
```

## Configuration

Open the `config.yaml` and set your OpenAI API key. Set any other configuration parameters as needed.

## Run the Streamlit test app

In the root folder, there is a Streamlit app that can be used to test the backend. Run the app using the following command:

```bash
streamlit run streamlit_app.py
```

This should launch a browser window with the Streamlit app. You can use the app to test the backend.

## Launch the web server

If you are using your own chat frontend, you can start the Flask web server using the following command:

```bash
python server.py
```
 ## Backend API

 You can integrate the consumer assistant backend into any other application (or build your own webservice) by using the following API functions from the `api.py` module:

- `chat(conversation_id)` - The main function to interact with the consumer assistant. It takes a conversation ID as input and returns a response from the assistant.

- `get_conversation(conversation_id)` - Get the conversation history for a given conversation ID.

- `list_conversations_for_user(user_id)` - Get a list of conversation IDs for a given user ID.

- `reset_conversation(conversation_id)` - Reset the conversation history for a given conversation ID.


[![CC BY 4.0][cc-by-shield]][cc-by]

This work is licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg