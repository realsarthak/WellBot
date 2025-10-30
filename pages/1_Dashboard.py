import streamlit as st
from db_functions import get_profile

# --- set_page_config() REMOVED FROM HERE ---

if not st.session_state.get('logged_in', False):
    st.warning("Please log in to view your dashboard.")
    st.stop()

with st.sidebar:
    st.title("Navigation")
    if st.button("Log Out"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.title("📊 Dashboard")
st.markdown("---")

profile_data = get_profile(st.session_state['user_id'])
if profile_data:
    name, age, language = profile_data
    st.header(f"Welcome back, {name if name else 'User'}!")
    st.info("💡 Go to the **Chat** page to ask health-related questions or visit the **Profile** page to update your information.")

    st.subheader("Your Current Profile")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="👤 Name", value=name if name else "Not set")
    col2.metric(label="🎂 Age", value=age if age else "Not set")
    col3.metric(label="🌐 Language", value=language)
else:
    st.error("Could not retrieve profile data.")