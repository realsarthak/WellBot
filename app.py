import streamlit as st
from db_functions import init_db, authenticate_user, add_user

st.set_page_config(
    page_title="Global Wellness Chatbot", 
    page_icon="🤖", 
    layout="centered",
    initial_sidebar_state="auto"
)

init_db()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = 'login'
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None

if st.session_state['logged_in']:
    st.success("You are logged in!")
    st.markdown("---")
    st.markdown("### Welcome to the Global Wellness Chatbot")
    st.write("Please use the navigation panel on the left to start a chat or manage your profile.")
    st.sidebar.success("Logged in successfully.")

else:
    st.title("Welcome to the Global Wellness Chatbot 🤖")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("---")
        if st.session_state['page'] == 'login':
            st.subheader("Sign In")
            with st.form("login_form"):
                email = st.text_input("📧 Email")
                password = st.text_input("🔒 Password", type="password")
                submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

                if submitted:
                    user_id = authenticate_user(email, password)
                    if user_id:
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = user_id
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
            
            if st.button("Create a new account", use_container_width=True):
                st.session_state['page'] = 'register'
                st.rerun()

        elif st.session_state['page'] == 'register':
            st.subheader("Create a New Account")
            with st.form("register_form"):
                email = st.text_input("📧 Email")
                password = st.text_input("🔒 Password", type="password")
                submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

                if submitted:
                    if add_user(email, password):
                        st.success("Account created! Please sign in.")
                        st.session_state['page'] = 'login'
                        st.rerun()
                    else:
                        st.error("This email is already registered.")

            if st.button("Already have an account? Sign in", use_container_width=True):
                st.session_state['page'] = 'login'
                st.rerun()
        st.markdown("---")