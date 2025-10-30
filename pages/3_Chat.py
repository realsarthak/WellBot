import streamlit as st
from chatbot_logic import get_bot_response, CONFIG 

if not st.session_state.get('logged_in', False):
    st.warning("Please log in to start a chat.")
    st.stop()

with st.sidebar:
    st.title("Navigation")
    if st.button("Log Out"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.title("💬 Global Wellness Chatbot")
# --- UPDATED INFO TEXT ---
st.info("आप अंग्रेज़ी या हिंदी में पूछ सकते हैं। (You can ask in English or Hindi.)", icon="🌐")

if "messages" not in st.session_state:
    # --- UPDATED WELCOME MESSAGE ---
    st.session_state.messages = [
        {"role": "assistant", "content": CONFIG["responses"]["greeting_en"]}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about a health condition..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            bot_response = get_bot_response(prompt)
        st.markdown(bot_response)
    
    st.session_state.messages.append({"role": "assistant", "content": bot_response})