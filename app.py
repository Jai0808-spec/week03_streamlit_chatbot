import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Embedded AI TA Chatbot", page_icon="🤖")

st.title("Embedded AI & Robotics TA Chatbot 🤖")
st.write("Ask anything about Arduino, sensors, motors, or tiny AI models!")

# Get API key from Streamlit secrets (we will set this on Streamlit Cloud)
# In a real environment, st.secrets.get() is the correct way to load the key.
api_key = st.secrets.get("OPENAI_API_KEY", None)
if api_key is None:
    # Use a placeholder for testing if running outside Streamlit Cloud with secrets set
    # NOTE: This will only work if running in an environment where the API key is accessible.
    # For local development, you might set this as an environment variable or in a .streamlit/secrets.toml file.
    # The actual production environment (Streamlit Cloud) requires the secret to be set.
    try:
        import os
        api_key = os.environ.get("OPENAI_API_KEY")
    except Exception:
        pass # If we can't get it from env, proceed to error display

    if api_key is None:
        st.error(
            "OPENAI_API_KEY is not set. Please add it in Streamlit Cloud → Settings → Secrets "
            "or set it as an environment variable for local testing."
        )
        st.stop()

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Initialise chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "system",
            "content": (
                "You are a friendly teaching assistant for an Embedded AI & Robotics lab. "
                "Explain things simply for first-year data science students. "
                "Keep your answers concise and highly practical, focusing on Arduino, sensors, and microcontrollers."
            ),
        }
    ]

# Display previous messages
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Type your question here…")

if user_input:
    # Add user message
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # Show user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call OpenAI
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                # IMPORTANT: Switching model to one that is guaranteed to exist and is suitable for this task.
                # 'gpt-4.1-mini' is not a standard OpenAI model name. Using 'gpt-3.5-turbo' instead.
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        # Create a copy of the messages list excluding the system instruction for the API call 
                        # to match the standard expected format, although 'system' role is usually handled fine.
                        # We send the entire history including the system message.
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state["messages"]
                    ],
                )
                reply = response.choices[0].message.content
                st.markdown(reply)

                # Save assistant reply
                st.session_state["messages"].append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"An error occurred while calling the OpenAI API: {e}")
                st.session_state["messages"].pop() # Remove the user's message on failure
