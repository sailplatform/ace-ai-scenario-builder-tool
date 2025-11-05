"""
Configuration and session state management for the AI Scenario Builder Tool.
"""
import streamlit as st


def initialize_session_state():
    """Initialize session state variables"""
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {
            "course": {},
            "project": {},
            "audience": {},
            "additional_info": {},
        }
    if 'workflow_mode' not in st.session_state:
        st.session_state.workflow_mode = None  # 'new', 'existing_course', 'existing_module'


def get_default_form_data():
    """Return default form data structure"""
    return {
        "course": {},
        "project": {},
        "audience": {},
        "additional_info": {},
    }


def reset_session_state():
    """Reset session state to initial values"""
    st.session_state.current_step = 0
    st.session_state.workflow_mode = None
    st.session_state.form_data = get_default_form_data()


def get_page_config():
    """Return Streamlit page configuration"""
    return {
        "page_title": "AI Scenario Builder Tool",
        "page_icon": None,
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
