import streamlit as st
from config import initialize_session_state, get_page_config
from ui_components import get_custom_css, display_progress, display_header
from steps import (
    step_initial_selection,
    step_existing_content_selection,
    step_course_info,
    step_project_info,
    step_audience_info,
    step_style_pack,
    step_review_export,
    step_next_phase,
    step_scenario_generation,
    step_screen_management,
    step_image_generation,
    step_final_review
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
    
    # Route to appropriate step
    if st.session_state.current_step == 0:
        step_initial_selection()
    elif st.session_state.current_step == 0.5:
        step_existing_content_selection()
    elif st.session_state.current_step == 1:
        step_course_info()
    elif st.session_state.current_step == 2:
        step_project_info()
    elif st.session_state.current_step == 3:
        step_audience_info()
    elif st.session_state.current_step == 4:
        step_style_pack()
    elif st.session_state.current_step == 5:
        step_review_export()
    elif st.session_state.current_step == 6:
        step_next_phase()
    elif st.session_state.current_step == 7:
        step_scenario_generation()
    elif st.session_state.current_step == 8:
        step_screen_management()
    elif st.session_state.current_step == 9:
        step_image_generation()
    elif st.session_state.current_step == 10:
        step_final_review()

if __name__ == "__main__":
    main()
