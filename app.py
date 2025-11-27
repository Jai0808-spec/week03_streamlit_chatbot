import streamlit as st
from openai import OpenAI

# --- Configuration & Setup ---

st.set_page_config(page_title="Embedded AI TA Chatbot", page_icon="🤖", layout="wide")

st.title("Embedded AI & Robotics TA Chatbot 🤖")
st.write("Configure the TA's persona and model on the left, then start asking questions about Arduino, sensors, motors, or tiny AI models!")

# --- Sidebar for Interactive Settings ---

with st.sidebar:
    st.header("⚙️ Chat Settings")

    # 1. Model Selector
    selected_model = st.selectbox(
        "Select Model",
        options=["gpt-4o-mini", "gpt-3.5-turbo"],
        index=0,
        help="gpt-4o-mini is generally smarter and faster, gpt-3.5-turbo is more cost-effective."
    )

    # 2. Dynamic System Instruction
    default_persona = (
        "You are a friendly teaching assistant for an Embedded AI & Robotics lab. "
        "Explain things simply for first-year data science students. "
        "Keep your answers concise and highly practical, focusing on Arduino, sensors, and microcontrollers."
    )
    system_prompt = st.text_area(
        "TA Persona (System Instruction)",
        value=default_persona,
        height=200,
        help="This defines the AI's role and tone. Change it to make the TA act differently!"
    )

    # 3. Clear History Button
    if st.button("🗑️ Clear Chat History", type="primary"):
        # This will trigger the app to re-initialize session state below
        st.session_state["messages"] = []
        st.experimental_rerun()


# --- Core Logic ---

# Get API key from Streamlit secrets
api_key = st.secrets.get("OPENAI_API_KEY", None)
if api_key is None:
    try:
        import os
        api_key = os.environ.get("OPENAI_API_KEY")
    except Exception:
        pass
    
    if api_key is None:
        st.error(
            "OPENAI_API_KEY is not set. Please add it in Streamlit Cloud → Settings → Secrets "
            "or set it as an environment variable for local testing."
        )
        st.stop()

client = OpenAI(api_key=api_key)

# Initialise chat history or ensure the system prompt is up-to-date
if "messages" not in st.session_state or len(st.session_state["messages"]) == 0:
    # Always start with the dynamic system prompt
    st.session_state["messages"] = [
        {"role": "system", "content": system_prompt}
    ]
elif st.session_state["messages"][0]["role"] == "system":
    # Update the system prompt if the user changed it in the sidebar
    st.session_state["messages"][0]["content"] = system_prompt
else:
    # Fallback to ensure the first message is the system message
    st.session_state["messages"].insert(0, {"role": "system", "content": system_prompt})


# --- Display Chat History ---

# Note: We skip displaying the first message (the system instruction)
for msg in st.session_state["messages"][1:]:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# --- Chat Input and API Call ---

user_input = st.chat_input("Type your question here…")

if user_input:
    # 1. Add user message
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # 2. Show user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # 3. Call OpenAI and stream the response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Prepare messages list for API call (contains all history including system instruction)
            messages_for_api = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state["messages"]
            ]

            response = client.chat.completions.create(
                model=selected_model,
                messages=messages_for_api,
                stream=True, # Use streaming for better user experience
            )

            for chunk in response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌") # Add a blinking cursor effect

            message_placeholder.markdown(full_response) # Final response without cursor

            # 4. Save assistant reply
            st.session_state["messages"].append({"role": "assistant", "content": full_response})

        except Exception as e:
            error_message = f"An error occurred while calling the OpenAI API with model {selected_model}: {e}"
            st.error(error_message)
            st.session_state["messages"].pop() # Remove the user's message on API failure
