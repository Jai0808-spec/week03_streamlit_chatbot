import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Embedded AI TA Chatbot", page_icon="🤖")

st.title("Embedded AI & Robotics TA Chatbot 🤖")
st.write("Ask anything about Arduino, sensors, motors, or tiny AI models!")

# Get API key from Streamlit secrets (we will set this on Streamlit Cloud)
api_key = st.secrets.get("OPENAI_API_KEY", None)
if api_key is None:
    st.error("OPENAI_API_KEY is not set. Please add it in Streamlit Cloud → Settings → Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

# Initialise chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "system",
            "content": (
                "You are a friendly teaching assistant for an Embedded AI & Robotics lab. "
                "Explain things simply for first-year data science students."
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
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=st.session_state["messages"],
            )
            reply = response.choices[0].message.content
            st.markdown(reply)

    # Save assistant reply
    st.session_state["messages"].append({"role": "assistant", "content": reply})```
