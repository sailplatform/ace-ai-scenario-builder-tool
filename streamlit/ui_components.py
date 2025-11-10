"""
UI components and styling for the AI Scenario Builder Tool.
"""
import streamlit as st
import os

LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "ace_ai.png")

def get_custom_css():
    """Return custom CSS styles for the application"""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');
        :root {
            --carnegie-red: #C41230;
            --scots-rose: #A50034;
            --gold-thread: #FDB515;
            --green-thread: #7DAF42;
            --teal-thread: #00847F;
            --blue-thread: #002D72;
            --highlands-sky: #A4DDED;
            --iron-gray: #54565B;
            --soft-gray: #f4f4f4;
            --deep-black: #101820;
            --midnight: #1E1E25;
        }
        html, body, [class*="css"] {
            font-family: 'Open Sans', sans-serif !important;
            color: var(--deep-black);
            background-color: #ffffff;
        }
        .ace-header {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1.15rem;
            margin-bottom: 2rem;
        }
        .ace-header-logo svg {
            width: 78px;
            height: 78px;
        }
        .ace-header-text .title {
            font-size: 2.4rem;
            font-weight: 700;
            color: var(--deep-black);
            letter-spacing: -0.5px;
        }
        .ace-header-text .subtitle {
            font-size: 1.05rem;
            font-weight: 600;
            color: var(--iron-gray);
            letter-spacing: 0.4px;
        }
        .main-header {
            display:none;
        }
        .step-header {
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--carnegie-red);
            margin-top: 2rem;
            margin-bottom: 1rem;
            letter-spacing: 0.2px;
        }
        .step-description {
            font-size: 1.05rem;
            color: var(--iron-gray);
            margin-bottom: 1.5rem;
        }
        .success-box {
            background-color: rgba(125, 175, 66, 0.12);
            border: 1px solid rgba(125, 175, 66, 0.4);
            border-radius: 0.65rem;
            padding: 1rem;
            margin: 1rem 0;
            color: var(--deep-black);
        }
        .info-box {
            background-color: rgba(164, 221, 237, 0.25);
            border: 1px solid rgba(164, 221, 237, 0.6);
            border-radius: 0.65rem;
            padding: 1rem;
            margin: 1rem 0;
            color: var(--deep-black);
        }
        .stButton button {
            border-radius: 999px;
            padding: 0.6rem 1.6rem;
            font-weight: 600;
            border: none;
            background: linear-gradient(135deg, var(--carnegie-red), var(--scots-rose));
            color: #ffffff;
            box-shadow: 0 8px 18px rgba(196, 18, 48, 0.22);
        }
        .stButton button:hover {
            background: linear-gradient(135deg, var(--scots-rose), var(--carnegie-red));
            box-shadow: 0 10px 22px rgba(196, 18, 48, 0.28);
        }
        .stButton button[kind="secondary"] {
            background: #ffffff;
            color: var(--carnegie-red);
            border: 1px solid rgba(196, 18, 48, 0.32);
            box-shadow: none;
        }
        .stButton button[kind="secondary"]:hover {
            background: rgba(196, 18, 48, 0.08);
        }
        .stProgress > div > div > div {
            background: linear-gradient(90deg, var(--carnegie-red), var(--gold-thread));
        }
        .stSidebar {
            background: #ffffff;
        }
        .stSidebar .stMarkdown,
        .stSidebar .stText {
            color: var(--deep-black);
        }
        .ace-sidebar-highlight {
            background: rgba(196, 18, 48, 0.08);
            border-left: 4px solid var(--carnegie-red);
            padding: 0.8rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        textarea, input, select {
            border-radius: 10px !important;
            border: 1px solid rgba(16, 24, 32, 0.12) !important;
            box-shadow: none !important;
        }
        textarea:focus, input:focus {
            border: 1px solid var(--carnegie-red) !important;
            box-shadow: 0 0 0 1px rgba(196, 18, 48, 0.2) !important;
        }
        .st-expander > div:first-child {
            background: rgba(0, 45, 114, 0.07);
            border-radius: 10px;
        }
        .ace-badge {
            display:inline-flex;
            align-items:center;
            background: rgba(196, 18, 48, 0.08);
            color: var(--carnegie-red);
            padding: 0.15rem 0.6rem;
            border-radius:999px;
            font-size:0.75rem;
            font-weight:600;
            letter-spacing:0.35px;
        }
        .ace-nav {
            width:100%;
            max-width:960px;
            margin:0 auto;
        }
        .ace-nav button {
            font-size:1.8rem !important;
            padding:0.3rem 1.4rem !important;
            border-radius:999px !important;
        }
        .ace-nav-back button {
            font-size:0.95rem !important;
            padding:0.45rem 1.4rem !important;
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
            "Metadata & Actors",
            "Screen Generation",
            "Image Generation",
            "Final Preview",
        ]
        
        progress = (st.session_state.current_step - 1) / len(steps)
        st.progress(progress)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: bold;'>Step {st.session_state.current_step}: {steps[st.session_state.current_step-1]}</div>", unsafe_allow_html=True)


def display_header():
    """Display the main header and welcome message"""

    from streamlit.components.v1 import html

    # Use columns to position image and title side by side and centered
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.empty()
    with col2:
        inner_col1, inner_col2 = st.columns([1, 4])
        with inner_col1:
            st.image(str(LOGO_PATH), width=78)
        with inner_col2:
            st.markdown(
                """
                <div class="ace-header-text" style="display: flex; align-items: center; height: 100%;">
                    <div class="title">ACE AI Scenario Builder</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with col3:
        st.empty()
    st.markdown(
        """
        <div class="info-box">
            This tool will guide you through creating a complete project setup that helps you design engaging learning scenarios 
    and presentation content. Follow the steps below to build your customized scenario.
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_optional_details_modal():
    """Display a persistent modal/dialog for optional project details"""
    # Only show during and after step 1
    if st.session_state.current_step < 1:
        return
    
    # Create a button in the sidebar or at the top
    with st.sidebar:
        st.markdown("### Project Information")
        
        # Fixed course and module titles at the top
        course_title_display = st.session_state.form_data["course"].get("course_title", "Not Set")
        module_title_display = st.session_state.form_data["project"].get("module_title", "Not Set")
        
        st.info(f"**Course:** {course_title_display}")
        st.info(f"**Module:** {module_title_display}")
        
        # Required Information Section
        with st.expander("Required Information", expanded=False):
            # course_title = st.text_input(
            #     "What course or program is the scenario generation for?",
            #     value=st.session_state.form_data["course"].get("course_title", ""),
            #     help="So the scenario fits the subject and level of your learners.",
            #     key="modal_course_title",
            #     placeholder="Enter the course or program name, e.g., Introduction to Data Analysis"
            # )
            
            professional_domain = st.text_input(
                "What is the learner's professional domain?",
                value=st.session_state.form_data["audience"].get("professional_domain", ""),
                help="This helps shape the tone and professional context of the scenario.",
                key="modal_professional_domain",
                placeholder="e.g., Marketing professionals, Social media managers, Data analysts"
            )
            
            course_description = st.text_area(
                "What is a high-level course description?",
                value=st.session_state.form_data["course"].get("course_description", ""),
                help="Provide context about what the course covers overall.",
                height=100,
                key="modal_course_description",
                placeholder="e.g., This course teaches students how to use AI tools..."
            )
            
            # module_title = st.text_input(
            #     "Which topic or module should the scenario focus on?",
            #     value=st.session_state.form_data["project"].get("module_title", ""),
            #     help="So the scenario stays aligned with what learners are currently studying.",
            #     key="modal_module_title",
            #     placeholder="Write the topic or module name, e.g., Ethical Decision-Making"
            # )
            
            key_concept = st.text_area(
                "What is the key concept or learning objective that the scenario should highlight?",
                value=st.session_state.form_data["project"].get("key_concept", ""),
                help="This becomes the main idea or concept the scenario brings to life.",
                height=100,
                key="modal_key_concept",
                placeholder="List one or two key ideas, e.g., analyzing information to make a decision"
            )
            
            existing_challenge = st.text_area(
                "What do the learners already know about this topic?",
                value=st.session_state.form_data["project"].get("existing_challenge", ""),
                help="This helps set the right level of challenge.",
                height=100,
                key="modal_existing_challenge",
                placeholder="Mention what learners already understand, e.g., they know basic tools"
            )
        
        # Optional Details Section
        # with st.expander("Additional Information", expanded=False):
            # course_objectives = st.text_area(
            #     "Course Learning Objectives",
            #     value=st.session_state.form_data["course"].get("course_objectives", ""),
            #     help="List main learning objectives (one per line or comma separated)",
            #     height=100,
            #     key="optional_course_objectives"
            # )
            
            # module_description = st.text_area(
            #     "Module Description",
            #     value=st.session_state.form_data["project"].get("module_description", ""),
            #     help="Brief description of what this module covers",
            #     height=80,
            #     key="optional_module_description"
            # )
            
            # project_learning_objectives = st.text_area(
            #     "Project Learning Objectives",
            #     value=st.session_state.form_data["project"].get("project_learning_objectives", ""),
            #     help="Specific learning objectives for this project (one per line or separated by commas)",
            #     height=100,
            #     key="optional_project_objectives"
            # )
            
            # education_levels = [
            #     "middle_school", "high_school", "undergrad_intro", "undergrad_advanced", 
            #     "grad_course", "bootcamp", "professional", "other"
            # ]
            
            # education_level = st.selectbox(
            #     "Education Level",
            #     options=education_levels,
            #     index=education_levels.index(st.session_state.form_data["audience"].get("education_level", "undergrad_intro")),
            #     help="Select the most appropriate education level",
            #     key="optional_education_level"
            # )
            
            # prerequisites = st.text_area(
            #     "Prerequisites",
            #     value=st.session_state.form_data["audience"].get("prerequisites", ""),
            #     help="List all prerequisites (one per line or separated by commas)",
            #     height=100,
            #     key="optional_prerequisites"
            # )
            
            # class_size = st.number_input(
            #     "Class Size",
            #     min_value=1,
            #     max_value=1000,
            #     value=st.session_state.form_data["audience"].get("class_size", 25),
            #     help="Expected number of students",
            #     key="optional_class_size"
            # )

        additional_info = st.text_area(
            "Additional Information",
            value=st.session_state.form_data["audience"].get("additional_info", ""),
            help="Additional information about the project",
            height=100,
            key="optional_additional_info"
        )
    
        st.markdown("")
        if st.button("Save All Details", type="primary", use_container_width=True):
            if not course_title or not professional_domain or not course_description or not module_title or not key_concept or not existing_challenge:
                st.error("All required fields must be filled.")
            else:
                st.session_state.form_data["course"]["course_title"] = course_title
                st.session_state.form_data["course"]["course_description"] = course_description
                st.session_state.form_data["project"]["module_title"] = module_title
                st.session_state.form_data["project"]["key_concept"] = key_concept
                st.session_state.form_data["project"]["existing_challenge"] = existing_challenge
                st.session_state.form_data["audience"]["professional_domain"] = professional_domain
                st.session_state.form_data["additional_info"] = additional_info
                
                # Save to JSON file
                try:
                    from utils import save_to_json
                    filepath = save_to_json()
                    st.success(f"Details saved to {filepath}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving details: {str(e)}")

        # Show final scenario for step 4+
        if st.session_state.current_step >= 4:
            st.markdown("---")
            st.subheader("Final Scenario")
            final_scenario = st.session_state.get("scenario_data", {}).get("final_scenario", "")
            
            updated_scenario = st.text_area(
                "Edit scenario:",
                value=final_scenario,
                height=120,
                key="sidebar_scenario_edit"
            )
            
            if st.button("Update Scenario", use_container_width=True):
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
                    
                    st.success("Scenario updated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            
            
            
            # Show metadata and actors for step 5+
            if st.session_state.current_step >= 5:
                st.markdown("---")
                st.subheader("Metadata & Actors")
                with st.expander("Metadata & Actors"):
                    metadata = st.session_state.get("metadata_data", {})
                    print(metadata)
                    if metadata:
                        num_screens = st.number_input("Number of Screens", value=metadata.get("num_screens", 5), key="sidebar_num_screens", min_value=1, max_value=20)
                        aspect_ratio = st.text_input("Aspect Ratio", value=metadata.get("aspect_ratio", "16:9"), key="sidebar_aspect_ratio")
                        visual_style = st.text_input("Visual Style", value=metadata.get("visual_style", "A vibrant, semi-realistic digital illustration in a modern vector art style, with soft gradients, clean lines, and cinematic lighting."), key="sidebar_visual_style")
                        
                        actors = metadata.get("actors", [])
                        st.markdown("**Actors:**")
                        for i, actor in enumerate(actors):
                            st.markdown(f"**Actor {i+1}: {actor.get('name', '')}**")
                            st.text_input(
                                "Name",
                                value=actor.get("name", ""),
                                key=f"sidebar_actor_{i}_name"
                            )
                            st.text_input(
                                "Role",
                                value=actor.get("role", ""),
                                key=f"sidebar_actor_{i}_role"
                            )
                            st.text_area(
                                "Purpose",
                                value=actor.get("purpose", ""),
                                key=f"sidebar_actor_{i}_purpose",
                                height=80
                            )
                            st.text_area(
                                "Appearance",
                                value=actor.get("appearance", ""),
                                key=f"sidebar_actor_{i}_appearance",
                                height=80
                            )
                            st.markdown("---")

                        if st.button("Update Metadata & Actors", use_container_width=True):
                            try:
                                actors_data = []
                                for i in range(len(actors)):
                                    actors_data.append({
                                        "name": st.session_state[f"sidebar_actor_{i}_name"],
                                        "role": st.session_state[f"sidebar_actor_{i}_role"],
                                        "purpose": st.session_state[f"sidebar_actor_{i}_purpose"],
                                        "appearance": st.session_state.get(f"sidebar_actor_{i}_appearance", "")
                                    })
                                st.session_state.metadata_data.update({
                                    "num_screens": num_screens,
                                    "aspect_ratio": aspect_ratio,
                                    "visual_style": visual_style,
                                    "actors": actors_data
                                })
                                
                                course_title = st.session_state.form_data["course"].get("course_title", "")
                                module_title = st.session_state.form_data["project"].get("module_title", "")
                                course_name = "".join(c for c in course_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
                                module_name = "".join(c for c in module_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
                                metadata_filepath = f"data/{course_name}/{module_name}/text_outputs/scenario_metadata.json"
                                import os
                                os.makedirs(os.path.dirname(metadata_filepath), exist_ok=True)
                                import json
                                with open(metadata_filepath, 'w') as f:
                                    json.dump(st.session_state.metadata_data, f, indent=2)
                                
                                st.success("Updated!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
            
            # Show screens for step 6+
            if st.session_state.current_step >= 6:
                st.markdown("---")
                st.subheader("Screens")
                with st.expander("Screens", expanded=False):
                    screens = st.session_state.get("screen_data", {}).get("screens", [])
                    if screens:
                        for i, screen in enumerate(screens):
                            st.markdown(f"**Screen {i+1}**")
                            caption = st.text_area(f"Caption", value=screen.get("caption", ""), key=f"sidebar_screen_{i}_caption", height=68, label_visibility="collapsed")
                            img_desc = st.text_area(f"Image Desc", value=screen.get("image_description", ""), key=f"sidebar_screen_{i}_img", height=80, label_visibility="collapsed")
                            
                            if st.button(f"Update Screen {i+1}", key=f"update_screen_{i}", use_container_width=True):
                                screens[i]["caption"] = caption
                                screens[i]["image_description"] = img_desc
                                course_title = st.session_state.form_data["course"].get("course_title", "")
                                module_title = st.session_state.form_data["project"].get("module_title", "")
                                course_name = "".join(c for c in course_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
                                module_name = "".join(c for c in module_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
                                screens_filepath = f"data/{course_name}/{module_name}/text_outputs/screens.json"
                                import os
                                os.makedirs(os.path.dirname(screens_filepath), exist_ok=True)
                                import json
                                with open(screens_filepath, 'w') as f:
                                    json.dump({"screens": screens}, f, indent=2)
                                st.session_state.screen_data = {"screens": screens}
                                st.rerun()
                            st.markdown("---")
        
