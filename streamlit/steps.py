"""
Step functions for the AI Scenario Builder Tool workflow.
"""
import json
import os
import streamlit as st
import openai
from utils import get_existing_courses, get_existing_modules, save_to_json
from config import get_default_form_data
from scenario_writer import (
    generate_scenario_description,
    generate_image_vibe,
    generate_initial_screens,
    generate_image_description_from_caption,
    save_scenario_data,
    load_scenario_data,
    get_scenario_filepath
)


def generate_scenario_summaries_with_gpt(form_data, existing_scenario_data):
    """
    Generate three short scenario summaries using GPT-4.1 based on form data and existing scenario data.
    """
    try:
        # Set up OpenAI client
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Extract key information from form data
        # Extract all fields present in example context.json and include if they exist
        # Course information
        course_title = form_data.get("course", {}).get("course_title", "")
        course_objectives = form_data.get("course", {}).get("course_objectives", "")

        # Project/module information
        module_title = form_data.get("project", {}).get("module_title", "")
        module_description = form_data.get("project", {}).get("module_description", "")
        project_title = form_data.get("project", {}).get("project_title", "")
        project_goal = form_data.get("project", {}).get("project_goal", "")
        project_learning_objectives = form_data.get("project", {}).get("project_learning_objectives", "")

        # Audience information
        student_description = form_data.get("audience", {}).get("student_description", "")
        education_level = form_data.get("audience", {}).get("education_level", "")
        prerequisites = form_data.get("audience", {}).get("prerequisites", "")
        class_size = form_data.get("audience", {}).get("class_size", "")
        audience_additional_info = form_data.get("audience", {}).get("additional_info", "")

        # Style pack information
        palette = form_data.get("style_pack", {}).get("palette", "")
        vibe = form_data.get("style_pack", {}).get("vibe", "")
        aspect_ratio = form_data.get("style_pack", {}).get("aspect_ratio", "")

        # General additional_info (not audience)
        additional_info = form_data.get("additional_info", "")

        
        # Extract existing scenario context if available
        existing_description = existing_scenario_data.get("scenario_description", "") if existing_scenario_data else ""
        
        # Create the prompt for GPT-4.1
        prompt = f"""
You are an expert educational scenario designer. Based on the following course and project information, generate exactly 3 short, engaging scenario summaries that would motivate students to complete this project.

Course: {course_title}
Course Objectives: {course_objectives}

Module Title: {module_title}
Module Description: {module_description}

Project Title: {project_title}
Project Goal: {project_goal}
Project Learning Objectives: {project_learning_objectives}

Student Profile: {student_description}
Education Level: {education_level}
Prerequisites: {prerequisites}
Class Size: {class_size}

Palette: {palette}
Vibe: {vibe}
Aspect Ratio: {aspect_ratio}

Additional Information: {additional_info}

Existing Scenario Context: {existing_description}

Generate 3 distinct scenario summaries (2-3 sentences long) that:
1. Are realistic and relatable to the target student audience
2. Present a clear challenge or problem to solve
3. Connect to the project goals and learning objectives
4. Are engaging and motivating
5. Are appropriate for the education level
6. Include DIVERSE characters (represent different ethnicities, genders, ages, backgrounds)
7. Specify the backdrop/setting where the scenario takes place

IMPORTANT: Each scenario must:
- Include diverse characters (avoid only white/male characters)
- Specify the setting/backdrop (e.g., "in a tech startup", "at a community center", "in a research lab")
- Keep character details brief - focus on the setting context, not detailed expressions

Format your response as:
SCENARIO 1: [summary with diverse characters and setting]
SCENARIO 2: [summary with diverse characters and setting] 
SCENARIO 3: [summary with diverse characters and setting]
"""
        
        # Call GPT-4.1
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",  # GPT-4.1 model
            messages=[
                {"role": "system", "content": """You are an expert educational scenario designer who creates engaging, realistic scenarios for student projects. 

CONTEXT EXAMPLE: safeChats is a fast-growing social media platform with active users worldwide. Their Trust and Safety team needs help strengthening content moderation systems and reducing costs. Currently, they use traditional sentiment analysis that flags posts as hate speech or not, but provides no explanations. Users complain about unfair flagging, and human reviewers spend extra time interpreting decisions. Their system also performs poorly in other languages. They're exploring Generative AI and LLMs because these can understand context, sarcasm, and nuance in multiple languages, explain reasoning in natural language, suggest better moderation responses, and continuously improve through feedback loops.

Your scenarios should focus on the overall setting context, like the example above, not detailed character descriptions."""},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        # Parse the response
        content = response.choices[0].message.content
        
        # Extract the three scenarios
        scenarios = []
        lines = content.split('\n')
        current_scenario = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith("SCENARIO 1:") or line.startswith("SCENARIO 2:") or line.startswith("SCENARIO 3:"):
                if current_scenario:
                    scenarios.append(current_scenario.strip())
                current_scenario = line.replace("SCENARIO 1:", "").replace("SCENARIO 2:", "").replace("SCENARIO 3:", "").strip()
            elif current_scenario and line:
                current_scenario += " " + line
        
        if current_scenario:
            scenarios.append(current_scenario.strip())
        
        # Ensure we have exactly 3 scenarios
        while len(scenarios) < 3:
            scenarios.append("Additional scenario could not be generated.")
        
        return scenarios[:3]
        
    except Exception as e:
        st.error(f"Error generating scenarios with GPT: {str(e)}")
        return [
            "Scenario generation failed. Please try again or contact support.",
            "Unable to generate scenario at this time.",
            "Error occurred during scenario generation."
        ]


def step_initial_selection():
    """Step 0: Initial Selection - Choose workflow mode"""
    st.markdown('<div class="step-header">🚀 Welcome to AI Scenario Builder</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-description">Choose how you\'d like to start your project.</div>', unsafe_allow_html=True)
    
    # Reset form data when returning to initial selection
    if st.session_state.workflow_mode is None or st.session_state.current_step == 0:
        st.session_state.form_data = get_default_form_data()
    
    # Check for existing courses
    existing_courses = get_existing_courses()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🆕 Create New Project")
        st.markdown("Start from scratch with a new course and module.")
        
        if st.button("Create New Project", type="primary", use_container_width=True):
            st.session_state.workflow_mode = "new"
            st.session_state.form_data = get_default_form_data()
            st.session_state.current_step = 1
            st.rerun()
    
    with col2:
        st.subheader("📚 Use Existing Content")
        if existing_courses:
            st.markdown("Build upon existing courses and modules.")
            
            if st.button("Use Existing Content", type="secondary", use_container_width=True):
                st.session_state.workflow_mode = "existing"
                st.session_state.form_data = get_default_form_data()
                st.session_state.current_step = 0.5  # Special step for existing content selection
                st.rerun()
        else:
            st.markdown("No existing courses found.")
            st.button("Use Existing Content", disabled=True, use_container_width=True)
    
    # Show existing courses if any
    if existing_courses:
        st.markdown("---")
        st.subheader("📁 Existing Courses")
        st.markdown("Found the following existing courses:")
        
        for course in existing_courses:
            modules = get_existing_modules(course)
            with st.expander(f"📚 {course} ({len(modules)} modules)"):
                if modules:
                    st.markdown("**Existing modules:**")
                    for module in modules:
                        st.markdown(f"  • {module}")
                else:
                    st.markdown("No modules found for this course.")


def step_existing_content_selection():
    """Step 0.5: Select existing course and module"""
    st.markdown('<div class="step-header">📚 Select Existing Content</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-description">Choose an existing course and module to build upon. After loading, you\'ll proceed directly to scenario generation.</div>', unsafe_allow_html=True)

    existing_courses = get_existing_courses()
    if not existing_courses:
        st.error("No existing courses found. Please create a new project.")
        if st.button("← Back to Selection"):
            st.session_state.workflow_mode = None
            st.session_state.form_data = get_default_form_data()
            st.session_state.current_step = 0
            st.rerun()
        return

    # Initialize single sources of truth
    if "selected_course" not in st.session_state or st.session_state.selected_course not in existing_courses:
        st.session_state.selected_course = existing_courses[0]
    if "selected_module" not in st.session_state:
        st.session_state.selected_module = None

    def _on_course_change():
        # Clear module whenever course changes
        st.session_state.selected_module = None

    st.subheader("Course Selection")
    # Single key, no manual assignment after rendering
    st.selectbox(
        "Select Course",
        options=existing_courses,
        index=existing_courses.index(st.session_state.selected_course) if st.session_state.selected_course in existing_courses else 0,
        key="selected_course",
        on_change=_on_course_change,
        help="Choose an existing course to build upon"
    )

    # Modules depend on the current course
    modules_for_course = get_existing_modules(st.session_state.selected_course)

    st.subheader("Module Selection")
    if modules_for_course:
        # Ensure module value is valid for this course
        if st.session_state.selected_module not in modules_for_course:
            st.session_state.selected_module = modules_for_course[0]

        st.selectbox(
            "Select Module",
            options=modules_for_course,
            index=modules_for_course.index(st.session_state.selected_module) if st.session_state.selected_module in modules_for_course else 0,
            key="selected_module",
            help="Choose an existing module"
        )
    else:
        st.warning("No modules found for the selected course.")
        st.session_state.selected_module = None

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Selection", type="secondary"):
            st.session_state.workflow_mode = None
            st.session_state.form_data = get_default_form_data()
            st.session_state.current_step = 0
            st.rerun()

    with col2:
        if st.button("Continue →", type="primary"):
            if not st.session_state.selected_module:
                st.error("Please select a module to continue.")
                return

            course_name_clean = st.session_state.selected_course.lower().replace(' ', '_')
            module_name_clean = st.session_state.selected_module.lower().replace(' ', '_')
            config_path = os.path.join(
                "data", course_name_clean, module_name_clean, "text_outputs", "context.json"
            )

            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        existing_data = json.load(f)
                    st.session_state.form_data = existing_data
                    st.session_state.workflow_mode = "existing_module"
                    st.info("✅ Configuration loaded! Proceeding to scenario generation...")
                    st.session_state.current_step = 3
                    st.session_state.scenarios_need_generation = True
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Could not load existing configuration: {str(e)}")
            else:
                st.error("❌ No existing configuration found for this module. Please create a new project instead.")

def step_project_setup():
    """Step 1: Combined Project Setup - All required information in one place"""
    st.markdown('<div class="step-header">🚀 Project Setup</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="step-description">Let\'s set up your project with the essential information.</div>', unsafe_allow_html=True)
    
    with st.form("project_setup_form"):
        st.subheader("Course & Module")
        
        course_title = st.text_input(
            "Course Title *",
            value=st.session_state.form_data["course"].get("course_title", ""),
            help="Enter the name of your course"
        )
        
        module_title = st.text_input(
            "Module Title *",
            value=st.session_state.form_data["project"].get("module_title", ""),
            help="Name of the module this project belongs to"
        )
        
        st.subheader("Project Details")
        
        project_title = st.text_input(
            "Project Title *",
            value=st.session_state.form_data["project"].get("project_title", ""),
            help="Name of the specific project"
        )
        
        project_goal = st.text_area(
            "Project Goal *",
            value=st.session_state.form_data["project"].get("project_goal", ""),
            help="What should students achieve by completing this project?",
            height=100
        )
        
        st.subheader("Student Profile")
        
        student_description = st.text_area(
            "Brief Student Description *",
            value=st.session_state.form_data["audience"].get("student_description", ""),
            help="Briefly describe who your students are (background, experience level, etc.)",
            placeholder="e.g., Army veterans with limited computer science experience",
            height=100
        )
        
        st.markdown("---")
        st.markdown("💡 **Tip:** You can add optional details like course objectives, learning objectives, education level, prerequisites, and class size at any time, using the sidebar.")
        
        submitted = st.form_submit_button("Continue to Review →", type="primary")
        
        if submitted:
            if all([course_title, module_title, project_title, project_goal, student_description]):
                # Save all data with defaults for optional fields
                st.session_state.form_data["course"] = {
                    "course_title": course_title,
                    "course_objectives": st.session_state.form_data["course"].get("course_objectives", "")
                }
                st.session_state.form_data["project"] = {
                    "module_title": module_title,
                    "module_description": st.session_state.form_data["project"].get("module_description", ""),
                    "project_title": project_title,
                    "project_goal": project_goal,
                    "project_learning_objectives": st.session_state.form_data["project"].get("project_learning_objectives", "")
                }
                st.session_state.form_data["audience"] = {
                    "student_description": student_description,
                    "education_level": st.session_state.form_data["audience"].get("education_level", "undergrad_intro"),
                    "prerequisites": st.session_state.form_data["audience"].get("prerequisites", ""),
                    "class_size": st.session_state.form_data["audience"].get("class_size", 25)
                }
                st.session_state.current_step = 2
                st.rerun()
            else:
                st.error("Please fill in all required fields (marked with *)")

def step_review_export():
    """Step 2: Review and Save Configuration"""
    st.markdown('<div class="step-header">📋 Review & Save Configuration</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-description">Review your information and save the configuration. Next, you\'ll generate AI-powered scenario descriptions for your project.</div>', unsafe_allow_html=True)
    
    # Display all collected information
    st.subheader("📚 Course Information")
    course_data = st.session_state.form_data["course"]
    st.markdown(f"**Course Title:** {course_data.get('course_title', 'Not provided')}")
    if course_data.get('course_objectives'):
        st.markdown(f"**Course Objectives:** {course_data.get('course_objectives', 'Not provided')}")
    
    st.subheader("🎯 Project Information")
    project_data = st.session_state.form_data["project"]
    st.markdown(f"**Module Title:** {project_data.get('module_title', 'Not provided')}")
    if project_data.get('module_description'):
        st.markdown(f"**Module Description:** {project_data.get('module_description', 'Not provided')}")
    st.markdown(f"**Project Title:** {project_data.get('project_title', 'Not provided')}")
    st.markdown(f"**Project Goal:** {project_data.get('project_goal', 'Not provided')}")
    if project_data.get('project_learning_objectives'):
        st.markdown(f"**Project Learning Objectives:** {project_data.get('project_learning_objectives', 'Not provided')}")
    
    st.subheader("👥 Audience")
    audience_data = st.session_state.form_data["audience"]
    st.markdown(f"**Student Description:** {audience_data.get('student_description', 'Not provided')}")
    st.markdown(f"**Education Level:** {audience_data.get('education_level', 'Not provided')}")
    if audience_data.get('prerequisites'):
        st.markdown(f"**Prerequisites:** {audience_data.get('prerequisites', 'Not provided')}")
    if audience_data.get('class_size'):
        st.markdown(f"**Class Size:** {audience_data.get('class_size')}")
    
    # Save and continue options
    st.subheader("💾 Save Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Project Setup", type="secondary"):
            st.session_state.current_step = 1
            st.rerun()
    
    with col2:
        if st.button("💾 Save & Generate Scenarios", type="primary"):
            try:
                filepath = save_to_json()
                st.success(f"✅ Configuration saved successfully!")
                st.info(f"📁 Saved to: `{filepath}`")
                
                # Move directly to scenario generation
                st.session_state.current_step = 3
                st.session_state.scenarios_need_generation = True
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error saving configuration: {str(e)}")
    
    with col3:
        if st.button("🔄 Start Over", type="secondary"):
            st.session_state.current_step = 0
            st.session_state.workflow_mode = None
            st.session_state.form_data = get_default_form_data()
            st.rerun()
    
    # Display JSON preview
    # st.subheader("📄 Configuration Preview")
    # st.json(st.session_state.form_data)

def step_scenario_generation():
    """Step 3: Generate Scenario Description and Image Vibe"""
    st.markdown('<div class="step-header">📝 Scenario Generation</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-description">Generate three scenario options using AI and select the best one for your project.</div>', unsafe_allow_html=True)
    
    # Check if scenario data already exists
    scenario_filepath = get_scenario_filepath(st.session_state.form_data)
    existing_scenario_data = load_scenario_data(scenario_filepath)
    
    # Initialize scenario data if not exists
    if not hasattr(st.session_state, 'scenario_data') or not st.session_state.scenario_data:
        st.session_state.scenario_data = existing_scenario_data or {}
    
    # Initialize generation flag if not exists
    if "scenarios_need_generation" not in st.session_state:
        st.session_state.scenarios_need_generation = True
    
    # Only generate new scenarios when flag is True
    if st.session_state.scenarios_need_generation:
        with st.spinner("🤖 Generating scenario options with AI..."):
            try:
                scenarios = generate_scenario_summaries_with_gpt(st.session_state.form_data, existing_scenario_data)
                st.session_state.scenario_data["generated_scenarios"] = scenarios
                st.session_state.scenario_data["selected_scenario"] = None
                st.session_state.scenarios_need_generation = False
            except Exception as e:
                st.error(f"❌ Error generating scenarios: {str(e)}")
                return
    
    # Display the three scenario options
    st.subheader("🎯 Choose Your Scenario")
    st.markdown("Select one of the AI-generated scenarios below, or edit it to better fit your needs:")
    
    scenarios = st.session_state.scenario_data.get("generated_scenarios", [])
    selected_scenario = st.session_state.scenario_data.get("selected_scenario", None)
    
    # Display scenarios in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Scenario Option 1**")
        if st.button("Select Option 1", key="select_1", type="primary" if selected_scenario == 0 else "secondary"):
            st.session_state.scenario_data["selected_scenario"] = 0
            st.rerun()
        st.info(scenarios[0] if len(scenarios) > 0 else "No scenario available")
    
    with col2:
        st.markdown("**Scenario Option 2**")
        if st.button("Select Option 2", key="select_2", type="primary" if selected_scenario == 1 else "secondary"):
            st.session_state.scenario_data["selected_scenario"] = 1
            st.rerun()
        st.info(scenarios[1] if len(scenarios) > 1 else "No scenario available")
    
    with col3:
        st.markdown("**Scenario Option 3**")
        if st.button("Select Option 3", key="select_3", type="primary" if selected_scenario == 2 else "secondary"):
            st.session_state.scenario_data["selected_scenario"] = 2
            st.rerun()
        st.info(scenarios[2] if len(scenarios) > 2 else "No scenario available")
    
    # Show selected scenario and allow editing
    if selected_scenario is not None:
        st.markdown("---")
        st.subheader("✏️ Edit Your Selected Scenario")
        
        # Text area for editing the selected scenario
        edited_scenario = st.text_area(
            "Edit your scenario:",
            value=scenarios[selected_scenario] if selected_scenario < len(scenarios) else "",
            height=100,
            key="edit_scenario"
        )
        
        # Update the scenario data
        if edited_scenario != scenarios[selected_scenario]:
            st.session_state.scenario_data["generated_scenarios"][selected_scenario] = edited_scenario
            st.session_state.scenario_data["final_scenario"] = edited_scenario
        
        # LLM-based editing
        st.markdown("**🤖 Or use AI to refine your scenario:**")
        update_instructions = st.text_area(
            "Describe how you'd like to modify the scenario:",
            placeholder="e.g., Make it more technical, add more diversity, focus on practical applications",
            height=80,
            key="llm_update_instructions"
        )
        
        if st.button("✨ Update with AI", type="secondary"):
            if update_instructions:
                with st.spinner("🤖 Updating scenario with AI..."):
                    try:
                        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                        response = client.chat.completions.create(
                            model="gpt-4-1106-preview",
                            messages=[
                                {"role": "system", "content": "You are an expert educational scenario designer. Update the given scenario based on the user's instructions while maintaining its core educational value."},
                                {"role": "user", "content": f"Current scenario: {edited_scenario}\n\nUpdate instructions: {update_instructions}\n\nProvide only the updated scenario text, no explanations."}
                            ],
                            max_tokens=500,
                            temperature=0.7
                        )
                        updated_scenario = response.choices[0].message.content.strip()
                        st.session_state.scenario_data["generated_scenarios"][selected_scenario] = updated_scenario
                        st.success("✅ Scenario updated with AI!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error updating scenario: {str(e)}")
            else:
                st.error("Please provide update instructions.")
        
        # Display final scenario
        st.subheader("📝 Final Scenario")
        st.success(edited_scenario)
    
    # Navigation buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Review", type="secondary"):
            st.session_state.current_step = 2
            st.rerun()
    
    with col2:
        if st.button("💾 Save & Continue", type="primary"):
            if selected_scenario is not None:
                try:
                    # Save scenario data
                    st.session_state.scenario_data["final_scenario"] = edited_scenario
                    save_scenario_data(st.session_state.scenario_data, scenario_filepath)
                    
                    # Also save to scenario_descriptions.json
                    course_title = st.session_state.form_data["course"].get("course_title", "")
                    module_title = st.session_state.form_data["project"].get("module_title", "")
                    course_name = "".join(c for c in course_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
                    module_name = "".join(c for c in module_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
                    desc_filepath = f"data/{course_name}/{module_name}/text_outputs/scenario_descriptions.json"
                    os.makedirs(os.path.dirname(desc_filepath), exist_ok=True)
                    with open(desc_filepath, 'w') as f:
                        json.dump({"scenario_description": edited_scenario}, f, indent=2)
                    
                    st.success("✅ Scenario saved successfully!")
                    st.session_state.current_step = 4
                    st.session_state.metadata_need_generation = True
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error saving scenario data: {str(e)}")
            else:
                st.error("Please select a scenario before saving.")
    
    with col3:
        if st.button("🔄 Generate New Options", type="secondary"):
            # Clear existing scenarios and regenerate
            if "scenario_data" in st.session_state:
                st.session_state.scenario_data.pop("generated_scenarios", None)
                st.session_state.scenario_data.pop("selected_scenario", None)
                st.session_state.scenario_data.pop("final_scenario", None)
            st.session_state.scenarios_need_generation = True
            st.rerun()


def step_scenario_metadata():
    """Step 4: Generate Scenario Metadata and Actors"""
    st.markdown('<div class="step-header">🎬 Scenario Metadata & Actors</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-description">Generate metadata and actors for your scenario using AI.</div>', unsafe_allow_html=True)
    
    # Initialize metadata generation flag
    if "metadata_need_generation" not in st.session_state:
        st.session_state.metadata_need_generation = True
    
    # Initialize metadata data if not exists
    if "metadata_data" not in st.session_state or not st.session_state.metadata_data:
        st.session_state.metadata_data = {}
    
    # Get final scenario
    final_scenario = st.session_state.scenario_data.get("final_scenario", "")
    
    # Generate metadata when flag is True
    if st.session_state.metadata_need_generation:
        with st.spinner("🤖 Generating scenario metadata with AI..."):
            try:
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                
                prompt = f"""Based on this scenario, generate metadata and actors:

Scenario: {final_scenario}

Course: {st.session_state.form_data["course"].get("course_title", "")}
Project: {st.session_state.form_data["project"].get("project_title", "")}

Generate:
1. Number of screens (typically 3-7)
2. Style pack (palette, vibe, aspect ratio)
3. Overall tone (e.g., professional, casual, technical)
4. List of 2-4 actors with: name, role, background, communication style

Format as JSON:
{{
  "num_screens": <number>,
  "style_pack": {{"palette": "", "vibe": "", "aspect_ratio": ""}},
  "overall_tone": "",
  "actors": [
    {{"name": "", "role": "", "background": "", "communication_style": ""}}
  ]
}}"""
                
                response = client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=[
                        {"role": "system", "content": "You are an expert educational content designer. Generate scenario metadata in valid JSON format."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=800,
                    temperature=0.7
                )
                
                import re
                content = response.choices[0].message.content
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    metadata = json.loads(json_match.group())
                    st.session_state.metadata_data = metadata
                    st.session_state.metadata_need_generation = False
                else:
                    st.error("Failed to parse metadata")
            except Exception as e:
                st.error(f"❌ Error generating metadata: {str(e)}")
                return
    
    # Display and edit metadata
    st.subheader("📊 Scenario Metadata")
    
    num_screens = st.number_input(
        "Number of Screens",
        min_value=1,
        max_value=20,
        value=st.session_state.metadata_data.get("num_screens", 5),
        key="edit_num_screens"
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        palette = st.text_input(
            "Color Palette",
            value=st.session_state.metadata_data.get("style_pack", {}).get("palette", ""),
            key="edit_palette"
        )
    with col2:
        vibe = st.text_input(
            "Visual Vibe",
            value=st.session_state.metadata_data.get("style_pack", {}).get("vibe", ""),
            key="edit_vibe"
        )
    with col3:
        aspect_ratio = st.text_input(
            "Aspect Ratio",
            value=st.session_state.metadata_data.get("style_pack", {}).get("aspect_ratio", "16:9"),
            key="edit_aspect_ratio"
        )
    
    overall_tone = st.text_input(
        "Overall Tone",
        value=st.session_state.metadata_data.get("overall_tone", ""),
        key="edit_tone"
    )
    
    # Display and edit actors
    st.subheader("🎭 Actors")
    
    actors = st.session_state.metadata_data.get("actors", [])
    if not actors:
        actors = [{"name": "", "role": "", "background": "", "communication_style": ""}]
    
    edited_actors = []
    for i, actor in enumerate(actors):
        with st.expander(f"Actor {i+1}: {actor.get('name', 'New Actor')}", expanded=True):
            name = st.text_input(f"Name", value=actor.get("name", ""), key=f"actor_{i}_name")
            role = st.text_input(f"Role", value=actor.get("role", ""), key=f"actor_{i}_role")
            background = st.text_area(f"Background", value=actor.get("background", ""), key=f"actor_{i}_background", height=80)
            comm_style = st.text_input(f"Communication Style", value=actor.get("communication_style", ""), key=f"actor_{i}_comm")
            edited_actors.append({
                "name": name,
                "role": role,
                "background": background,
                "communication_style": comm_style
            })
    
    if st.button("➕ Add Actor"):
        actors.append({"name": "", "role": "", "background": "", "communication_style": ""})
        st.session_state.metadata_data["actors"] = actors
        st.rerun()
    
    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Scenario", type="secondary"):
            st.session_state.current_step = 3
            st.rerun()
    
    with col2:
        if st.button("💾 Save Metadata", type="primary"):
            try:
                # Update metadata
                st.session_state.metadata_data.update({
                    "num_screens": num_screens,
                    "style_pack": {"palette": palette, "vibe": vibe, "aspect_ratio": aspect_ratio},
                    "overall_tone": overall_tone,
                    "actors": edited_actors
                })
                
                # Save to file
                course_title = st.session_state.form_data["course"].get("course_title", "")
                module_title = st.session_state.form_data["project"].get("module_title", "")
                course_name = "".join(c for c in course_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
                module_name = "".join(c for c in module_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
                metadata_filepath = f"data/{course_name}/{module_name}/text_outputs/scenario_metadata.json"
                os.makedirs(os.path.dirname(metadata_filepath), exist_ok=True)
                with open(metadata_filepath, 'w') as f:
                    json.dump(st.session_state.metadata_data, f, indent=2)
                
                st.success("✅ Metadata saved successfully!")
            except Exception as e:
                st.error(f"❌ Error saving metadata: {str(e)}")
    
    with col3:
        if st.button("🔄 Regenerate", type="secondary"):
            st.session_state.metadata_need_generation = True
            st.rerun()
