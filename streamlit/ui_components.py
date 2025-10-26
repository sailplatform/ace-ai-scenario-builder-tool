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
            "Project Setup",
            "Review & Save",
            "Scenario Generation",
            "Metadata & Actors"
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


def display_optional_details_modal():
    """Display a persistent modal/dialog for optional project details"""
    # Only show during and after step 1
    if st.session_state.current_step < 1:
        return
    
    # Create a button in the sidebar or at the top
    with st.sidebar:
        st.markdown("### 📝 Project Information")
        
        # Fixed course and module titles at the top
        course_title_display = st.session_state.form_data["course"].get("course_title", "Not Set")
        module_title_display = st.session_state.form_data["project"].get("module_title", "Not Set")
        
        st.info(f"**Course:** {course_title_display}")
        st.info(f"**Module:** {module_title_display}")
        
        # Required Information Section
        with st.expander("✏️ Required Information", expanded=False):
            project_title = st.text_input(
                "Project Title *",
                value=st.session_state.form_data["project"].get("project_title", ""),
                key="modal_project_title"
            )
            
            project_goal = st.text_area(
                "Project Goal *",
                value=st.session_state.form_data["project"].get("project_goal", ""),
                height=100,
                key="modal_project_goal"
            )
            
            student_description = st.text_area(
                "Brief Student Description *",
                value=st.session_state.form_data["audience"].get("student_description", ""),
                height=100,
                key="modal_student_description"
            )
        
        # Optional Details Section
        with st.expander("📋 Optional Details", expanded=False):
            course_objectives = st.text_area(
                "Course Learning Objectives",
                value=st.session_state.form_data["course"].get("course_objectives", ""),
                help="List main learning objectives (one per line or comma separated)",
                height=100,
                key="optional_course_objectives"
            )
            
            module_description = st.text_area(
                "Module Description",
                value=st.session_state.form_data["project"].get("module_description", ""),
                help="Brief description of what this module covers",
                height=80,
                key="optional_module_description"
            )
            
            project_learning_objectives = st.text_area(
                "Project Learning Objectives",
                value=st.session_state.form_data["project"].get("project_learning_objectives", ""),
                help="Specific learning objectives for this project (one per line or separated by commas)",
                height=100,
                key="optional_project_objectives"
            )
            
            education_levels = [
                "middle_school", "high_school", "undergrad_intro", "undergrad_advanced", 
                "grad_course", "bootcamp", "professional", "other"
            ]
            
            education_level = st.selectbox(
                "Education Level",
                options=education_levels,
                index=education_levels.index(st.session_state.form_data["audience"].get("education_level", "undergrad_intro")),
                help="Select the most appropriate education level",
                key="optional_education_level"
            )
            
            prerequisites = st.text_area(
                "Prerequisites",
                value=st.session_state.form_data["audience"].get("prerequisites", ""),
                help="List all prerequisites (one per line or separated by commas)",
                height=100,
                key="optional_prerequisites"
            )
            
            class_size = st.number_input(
                "Class Size",
                min_value=1,
                max_value=1000,
                value=st.session_state.form_data["audience"].get("class_size", 25),
                help="Expected number of students",
                key="optional_class_size"
            )

            additional_info = st.text_area(
                "Additional Information",
                value=st.session_state.form_data["audience"].get("additional_info", ""),
                help="Additional information about the project",
                height=100,
                key="optional_additional_info"
            )
        
        st.markdown("")
        if st.button("💾 Save All Details", type="primary", use_container_width=True):
            course_title = st.session_state.form_data["course"].get("course_title", "")
            module_title = st.session_state.form_data["project"].get("module_title", "")
            
            if not course_title or not module_title or not project_title or not project_goal or not student_description:
                st.error("❌ All required fields must be filled.")
            else:
                # Update form data with all fields
                st.session_state.form_data["course"]["course_objectives"] = course_objectives
                st.session_state.form_data["project"]["module_description"] = module_description
                st.session_state.form_data["project"]["project_title"] = project_title
                st.session_state.form_data["project"]["project_goal"] = project_goal
                st.session_state.form_data["project"]["project_learning_objectives"] = project_learning_objectives
                st.session_state.form_data["audience"]["student_description"] = student_description
                st.session_state.form_data["audience"]["education_level"] = education_level
                st.session_state.form_data["audience"]["prerequisites"] = prerequisites
                st.session_state.form_data["audience"]["class_size"] = class_size
                st.session_state.form_data["audience"]["additional_info"] = additional_info
                
                # Save to JSON file
                try:
                    from utils import save_to_json
                    filepath = save_to_json()
                    st.success(f"✅ Details saved to {filepath}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error saving details: {str(e)}")

        # Show final scenario for step 4+
        if st.session_state.current_step >= 4:
            st.markdown("---")
            st.subheader("📝 Final Scenario")
            final_scenario = st.session_state.get("scenario_data", {}).get("final_scenario", "")
            
            updated_scenario = st.text_area(
                "Edit scenario:",
                value=final_scenario,
                height=120,
                key="sidebar_scenario_edit"
            )
            
            if st.button("💾 Update Scenario", use_container_width=True):
                try:
                    st.session_state.scenario_data["final_scenario"] = updated_scenario
                    
                    # Save to scenario_descriptions.json
                    course_title = st.session_state.form_data["course"].get("course_title", "")
                    module_title = st.session_state.form_data["project"].get("module_title", "")
                    course_name = "".join(c for c in course_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
                    module_name = "".join(c for c in module_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
                    desc_filepath = f"data/{course_name}/{module_name}/text_outputs/scenario_descriptions.json"
                    
                    import os
                    os.makedirs(os.path.dirname(desc_filepath), exist_ok=True)
                    import json
                    with open(desc_filepath, 'w') as f:
                        json.dump({"scenario_description": updated_scenario}, f, indent=2)
                    
                    st.success("✅ Scenario updated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            
            st.markdown("---")
        
