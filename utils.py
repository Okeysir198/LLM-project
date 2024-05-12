import os

import openai  # type: ignore
import streamlit as st  # type: ignore

def enable_chat_history(func):
    """
    Decorator function that enables chat history for a function.

    This decorator checks for an OPENAI_API_KEY environment variable. If it exists, 
    it keeps track of the current page and chat history in the Streamlit session state.
    For each message in the chat history, it displays it using the streamlit.chat_message function.

    Args:
        func: The function to be decorated.

    Returns:
        A wrapper function that executes the decorated function and manages the chat history.
    """
    def execute(*args, **kwargs):
        if os.environ.get("OPENAI_API_KEY"):
            current_page = func.__qualname__
            if current_page != st.session_state.get("current_page"):
                try:
                    st.cache_resource.clear()
                    del st.session_state["current_page"]
                    del st.session_state["messages"]
                except KeyError:
                    pass
            if "messages" not in st.session_state:
                st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
            for msg in st.session_state["messages"]:
                st.chat_message(msg["role"]).write(msg["content"])
        return func(*args, **kwargs)
    return execute


def display_msg(msg, author):
    """
    Displays a message in the Streamlit chat interface.

    This function appends the message to the chat history in the Streamlit session state
    and then uses streamlit.chat_message to display it on the screen with the specified author.

    Args:
        msg: The message content to be displayed.
        author: The author of the message (e.g., "user" or "assistant").
    """
    st.session_state.messages.append({"role": author, "content": msg})
    st.chat_message(author).write(msg)


def configure_openai():
    """
    Configures the OpenAI API connection and selected model.

    This function retrieves the OpenAI API key from the Streamlit sidebar and sets it
    as an environment variable. It then attempts to connect to the OpenAI API and lists
    available GPT models. The user can select a model from the sidebar. The selected model
    and API key are stored in the Streamlit session state.

    Returns:
        The ID of the selected OpenAI LLM model.
    """
    openai_api_key = st.sidebar.text_input(
        label="OpenAI API Key",
        type="password",
        value=st.session_state.get('OPENAI_API_KEY'),
        placeholder="sk-..."
    )
    if openai_api_key:
        st.session_state['OPENAI_API_KEY'] = openai_api_key
        os.environ['OPENAI_API_KEY'] = openai_api_key
    else:
        st.error("An OpenAI API key is required to proceed.")
        st.info("To obtain an OpenAI API key, please visit the following link: https://platform.openai.com/account/api-keys")
        st.stop()

    try:
        client = openai.OpenAI()
        available_models = [i.id for i in client.models.list() if str(i.id).startswith("gpt")]
        selected_model = st.sidebar.selectbox(
            label="LLM Model",
            options=available_models,
            index=available_models.index(st.session_state.get('OPENAI_MODEL', "gpt-3.5-turbo-0125"))  # Default is "gpt-3.5-turbo-0125"
        )
        st.session_state['OPENAI_MODEL'] = selected_model
    except openai.AuthenticationError as e:
        st.error(e.body["message"])
        st.stop()
    except Exception as e:
        print(e)
        st.error("Something went wrong. Please try again later.")
        st.stop()
    return selected_model

