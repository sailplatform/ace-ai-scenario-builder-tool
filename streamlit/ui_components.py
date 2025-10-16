"""
UI components and styling for the AI Scenario Builder Tool.
"""
import streamlit as st


def get_custom_css():
    """Return custom CSS styles for the application"""
    return """
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .step-header {
            font-size: 1.8rem;
            font-weight: bold;
            color: #2e8b57;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        .step-description {
            font-size: 1.1rem;
            color: #666;
            margin-bottom: 1.5rem;
        }
        .success-box {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 1rem 0;
        }
        .info-box {
            background-color: #e7f3ff;
            border: 1px solid #b3d9ff;
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 1rem 0;
        }
    </style>
    """


def display_progress():
    """Display progress bar and current step"""
    if st.session_state.current_step == 0:
       return
    elif st.session_state.current_step == 0.5:
        st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: bold;'>Select Existing Content</div>", unsafe_allow_html=True)
    else:
        steps = [
            "Course Information",
            "Project Information", 
            "Audience Details",
            "Style Preferences",
            "Review & Save",
            "Next Phase",
            "Scenario Generation",
            "Screen Management",
            "Image Generation",
            "Final Review"
        ]
        
        progress = (st.session_state.current_step - 1) / len(steps)
        st.progress(progress)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: bold;'>Step {st.session_state.current_step}: {steps[st.session_state.current_step-1]}</div>", unsafe_allow_html=True)


def display_header():
    """Display the main header and welcome message"""
    st.markdown('<div class="main-header">🎯 AI Scenario Builder Tool</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
    <strong>Welcome!</strong> This tool will guide you through creating a comprehensive project configuration 
    that can be used to generate AI-assisted course scenarios and motivation slides. 
    Follow the steps below to build your project profile.
    </div>
    """, unsafe_allow_html=True)
