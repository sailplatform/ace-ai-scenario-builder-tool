import streamlit as st
from config import initialize_session_state, get_page_config
from ui_components import get_custom_css, display_progress, display_header, display_optional_details_modal
from steps import (
    step_initial_selection,
    step_existing_content_selection,
    step_project_setup,
    step_review_export,
    step_scenario_generation,
    step_scenario_metadata,
    step_screen_generation
)

# Page configuration
page_config = get_page_config()
st.set_page_config(**page_config)

# Custom CSS for better styling
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize session state
initialize_session_state()


# Main app
def main():
    # Display header
    display_header()
    
    # Display progress
    display_progress()
    
    # Display optional details modal (persists through all steps)
    display_optional_details_modal()
    
    # Route to appropriate step
    if st.session_state.current_step == 0:
        step_initial_selection()
    elif st.session_state.current_step == 0.5:
        step_existing_content_selection()
    elif st.session_state.current_step == 1:
        step_project_setup()
    elif st.session_state.current_step == 2:
        step_review_export()
    elif st.session_state.current_step == 3:
        step_scenario_generation()
    elif st.session_state.current_step == 4:
        step_scenario_metadata()
    elif st.session_state.current_step == 5:
        step_screen_generation()

if __name__ == "__main__":
    main()
