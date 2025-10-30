import streamlit as st
from db_functions import get_profile, update_profile

# --- set_page_config() REMOVED FROM HERE ---

if not st.session_state.get('logged_in', False):
    st.warning("Please log in to manage your profile.")
    st.stop()

with st.sidebar:
    st.title("Navigation")
    if st.button("Log Out"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.title("📝 Manage Your Profile")
current_profile = get_profile(st.session_state['user_id'])
if current_profile:
    current_name, current_age, current_language = current_profile

    with st.expander("Edit Your Information", expanded=True):
        with st.form("profile_form"):
            name = st.text_input("👤 Name", value=current_name)
            age = st.number_input("🎂 Age", min_value=1, max_value=120, value=current_age if current_age is not None else 25, step=1)
            language = st.selectbox("🌐 Language Preference", ["English", "Hindi"], index=["English", "Hindi"].index(current_language))
            submitted = st.form_submit_button("Save Changes", use_container_width=True, type="primary")

            if submitted:
                age_to_save = age if age > 0 else None
                update_profile(st.session_state['user_id'], name, age_to_save, language)
                st.toast("✅ Profile updated successfully!")
else:
    st.error("Could not load your profile.")