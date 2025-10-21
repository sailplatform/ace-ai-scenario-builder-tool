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
        course_title = form_data.get("course", {}).get("course_title", "")
        project_title = form_data.get("project", {}).get("project_title", "")
        project_goal = form_data.get("project", {}).get("project_goal", "")
        student_description = form_data.get("audience", {}).get("student_description", "")
        education_level = form_data.get("audience", {}).get("education_level", "")
        
        # Extract existing scenario context if available
        existing_description = existing_scenario_data.get("scenario_description", "") if existing_scenario_data else ""
        
        # Create the prompt for GPT-4.1
        prompt = f"""
You are an expert educational scenario designer. Based on the following course and project information, generate exactly 3 short, engaging scenario summaries that would motivate students to complete this project.

Course: {course_title}
Project: {project_title}
Project Goal: {project_goal}
Student Profile: {student_description}
Education Level: {education_level}

Existing Scenario Context: {existing_description}

Generate 3 distinct scenario summaries (2-3 sentences long) that:
1. Are realistic and relatable to the target student audience
2. Present a clear challenge or problem to solve
3. Connect to the project goals and learning objectives
4. Are engaging and motivating
5. Are appropriate for the education level
6. Include DIVERSE characters (represent different ethnicities, genders, ages, backgrounds)
7. Specify the backdrop/setting where the scenario takes place
8. Focus on LEARNING GOALS and real-world applications
9. Show how the scenario connects to practical, industry-relevant skills

IMPORTANT: Each scenario must:
- Include diverse characters (avoid only white/male characters)
- Specify the setting/backdrop (e.g., "in a tech startup", "at a community center", "in a research lab")
- Clearly connect to the learning objectives and real-world applications
- Explain how the scenario motivates learning and provides context for where skills are used
- Keep character details brief - focus on the learning connection, not detailed expressions

Format your response as:
SCENARIO 1: [summary with diverse characters, setting, and learning connection]
SCENARIO 2: [summary with diverse characters, setting, and learning connection] 
SCENARIO 3: [summary with diverse characters, setting, and learning connection]
"""
        
        # Call GPT-4.1
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",  # GPT-4.1 model
            messages=[
                {"role": "system", "content": """You are an expert educational scenario designer who creates engaging, realistic scenarios for student projects. 

CONTEXT EXAMPLE: safeChats is a fast-growing social media platform with active users worldwide. Their Trust and Safety team needs help strengthening content moderation systems and reducing costs. Currently, they use traditional sentiment analysis that flags posts as hate speech or not, but provides no explanations. Users complain about unfair flagging, and human reviewers spend extra time interpreting decisions. Their system also performs poorly in other languages. They're exploring Generative AI and LLMs because these can understand context, sarcasm, and nuance in multiple languages, explain reasoning in natural language, suggest better moderation responses, and continuously improve through feedback loops.

Your scenarios should focus on real-world applications and learning connections, not detailed character descriptions."""},
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
    
    
    # Check for existing courses
    existing_courses = get_existing_courses()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🆕 Create New Project")
        st.markdown("Start from scratch with a new course and module.")
        
        if st.button("Create New Project", type="primary", use_container_width=True):
            st.session_state.workflow_mode = "new"
            st.session_state.current_step = 1
            st.rerun()
    
    with col2:
        st.subheader("📚 Use Existing Content")
        if existing_courses:
            st.markdown("Build upon existing courses and modules.")
            
            if st.button("Use Existing Content", type="secondary", use_container_width=True):
                st.session_state.workflow_mode = "existing"
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
    st.markdown('<div class="step-description">Choose an existing course and module to build upon.</div>', unsafe_allow_html=True)
    
    existing_courses = get_existing_courses()
    
    if not existing_courses:
        st.error("No existing courses found. Please create a new project.")
        if st.button("← Back to Selection"):
            st.session_state.current_step = 0
            st.rerun()
        return
    
    with st.form("existing_content_form"):
        st.subheader("Course Selection")
        
        selected_course = st.selectbox(
            "Select Course",
            options=existing_courses,
            help="Choose an existing course to build upon"
        )
        
        st.subheader("Module Selection")
        
        existing_modules = get_existing_modules(selected_course)
        
        if existing_modules:
            selected_module = st.selectbox(
                "Select Module",
                options=existing_modules,
                help="Choose an existing module"
            )
        else:
            st.error("No existing modules found for this course. Please create a new project instead.")
            selected_module = None
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("← Back to Selection", type="secondary")
            if submitted:
                st.session_state.current_step = 0
                st.rerun()
        
        with col2:
            submitted = st.form_submit_button("Continue →", type="primary")
            if submitted:
                if not selected_module:
                    st.error("Please select a module to continue.")
                    return
                
                # Store the selected course and module
                st.session_state.selected_course = selected_course
                st.session_state.selected_module = selected_module
                
                # Try to load existing configuration
                course_name_clean = selected_course.lower().replace(' ', '_')
                module_name_clean = selected_module.lower().replace(' ', '_')
                config_path = os.path.join("data", course_name_clean, module_name_clean, "text_outputs", "module_generation_information.json")
                
                if os.path.exists(config_path):
                    try:
                        with open(config_path, 'r') as f:
                            existing_data = json.load(f)
                        st.session_state.form_data = existing_data
                        st.session_state.workflow_mode = "existing_module"
                        
                        # Skip directly to step 5 (Next Phase) since both course and module exist
                        st.session_state.current_step = 5
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Could not load existing configuration: {str(e)}")
                else:
                    st.error("❌ No existing configuration found for this module. Please create a new project instead.")


def step_course_info():
    """Step 1: Course Information"""
    st.markdown('<div class="step-header">📚 Course Information</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="step-description">Let\'s start with the basic course details that will provide context for your project.</div>', unsafe_allow_html=True)
    
    with st.form("course_info_form"):
        st.subheader("Course Details")
        
        course_title = st.text_input(
            "Course Title *",
            value=st.session_state.form_data["course"].get("course_title", ""),
            help="Enter the name of your course"
        )
        
        course_objectives = st.text_area(
            "Course Learning Objectives (Optional)",
            value=st.session_state.form_data["course"].get("course_objectives", ""),
            help="List main learning objectives (one per line or comma separated)",
            height=100
        )
        
        submitted = st.form_submit_button("Continue to Project Information", type="primary")
        
        if submitted:
            if course_title:
                st.session_state.form_data["course"] = {
                    "course_title": course_title,
                    "course_objectives": course_objectives
                }
                st.session_state.current_step = 2
                st.rerun()
            else:
                st.error("Please enter a course title")


def step_project_info():
    """Step 2: Project Information"""
    st.markdown('<div class="step-header">🎯 Project Information</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="step-description">Now let\'s define the specific project and module details.</div>', unsafe_allow_html=True)
    
    with st.form("project_info_form"):
        st.subheader("Module Details")
        
        module_title = st.text_input(
            "Module Title *",
            value=st.session_state.form_data["project"].get("module_title", ""),
            help="Name of the module this project belongs to"
        )
        
        module_description = st.text_area(
            "Module Description (Optional)",
            value=st.session_state.form_data["project"].get("module_description", ""),
            help="Brief description of what this module covers",
            height=80
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
            height=80
        )
        
        project_learning_objectives = st.text_area(
            "Project Learning Objectives (Optional)",
            value=st.session_state.form_data["project"].get("project_learning_objectives", ""),
            help="Specific learning objectives for this project (one per line or separated by commas)",
            height=100
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("← Back to Course Info", type="secondary")
            if submitted:
                st.session_state.current_step = 1
                st.rerun()
        
        with col2:
            submitted = st.form_submit_button("Continue to Audience →", type="primary")
            if submitted:
                if all([module_title, project_title, project_goal]):
                    st.session_state.form_data["project"] = {
                        "module_title": module_title,
                        "module_description": module_description,
                        "project_title": project_title,
                        "project_goal": project_goal,
                        "project_learning_objectives": project_learning_objectives
                    }
                    st.session_state.current_step = 3
                    st.rerun()
                else:
                    st.error("Please fill in module title, project title, and project goal")


def step_audience_info():
    """Step 3: Audience Information"""
    st.markdown('<div class="step-header">👥 Audience Information</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-description">Tell us about your students and their background.</div>', unsafe_allow_html=True)
    
    with st.form("audience_info_form"):
        st.subheader("Student Profile")
        
        student_description = st.text_area(
            "Student Description *",
            value=st.session_state.form_data["audience"].get("student_description", ""),
            help="Describe who your students are (background, experience level, etc.)",
            placeholder="e.g., Army veterans with limited computer science experience",
            height=80
        )
        
        education_levels = [
            "middle_school", "high_school", "undergrad_intro", "undergrad_advanced", 
            "grad_course", "bootcamp", "professional", "other"
        ]
        
        education_level = st.selectbox(
            "Education Level *",
            options=education_levels,
            index=education_levels.index(st.session_state.form_data["audience"].get("education_level", "undergrad_intro")),
            help="Select the most appropriate education level"
        )
        
        st.subheader("Prerequisites (Optional)")
        st.markdown("What should students know before starting this project?")
        
        # Single text area for all prerequisites
        prerequisites_text = st.text_area(
            "Prerequisites",
            value=st.session_state.form_data["audience"].get("prerequisites", ""),
            help="List all prerequisites (one per line or separated by commas)",
            height=100
        )
        
        st.subheader("Class Information")
        
        class_size = st.number_input(
            "Class Size (Optional)",
            min_value=1,
            max_value=1000,
            value=st.session_state.form_data["audience"].get("class_size", 25),
            help="Expected number of students"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("← Back to Project Info", type="secondary")
            if submitted:
                st.session_state.current_step = 2
                st.rerun()
        
        with col2:
            submitted = st.form_submit_button("Continue to Review →", type="primary")
            if submitted:
                if student_description and education_level:
                    st.session_state.form_data["audience"] = {
                        "student_description": student_description,
                        "education_level": education_level,
                        "prerequisites": prerequisites_text,
                        "class_size": class_size if class_size > 0 else None
                    }
                    st.session_state.current_step = 4
                    st.rerun()
                else:
                    st.error("Please fill in the student description and education level")


# def step_style_pack():
#     """Step 4: Style Preferences"""
#     st.markdown('<div class="step-header">🎨 Style Preferences</div>', unsafe_allow_html=True)
#     st.markdown('<div class="step-description">Define the visual style and additional information for your motivation slides.</div>', unsafe_allow_html=True)
    
#     with st.form("style_pack_form"):
#         st.subheader("Visual Style")
        
#         # Style reference guide
#         with st.expander("📚 Style Reference Guide", expanded=False):
#             st.markdown("""
#             **Common Color Palettes:**
#             - `cool contrast` - blue and teal, navy and cyan
#             - `warm contrast` - red and orange, coral and gold
#             - `vibrant duo` - purple and yellow, magenta and lime
#             - `earth duo` - brown and olive, tan and forest

#             **Visual Style Examples:**
#             - `comic panel style` - bold outlines, limited shading, expressive poses
#             - `flat illustration design` - simple shapes, clean fills, minimal detail
#             - `semi realistic rendering` - stylized proportions, moderate detail
#             - `photo realistic imagery` - lifelike textures, accurate lighting
#             - `minimalist visual language` - ample whitespace, few elements
#             - `hand drawn sketch style` - pencil or ink lines, textured strokes
#             - `three dimensional render` - modeled forms, perspective and lighting

#             **Aspect Ratios:**
#             - `4:3` - traditional presentation format
#             - `16:9` - widescreen format
#             - `1:1` - square format
#             - `3:2` - photo format
#             """)
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             palette = st.text_input(
#                 "Color Palette",
#                 value=st.session_state.form_data["style_pack"].get("palette", "blue"),
#                 help="Enter your preferred color palette (see reference guide above)"
#             )
            
#             vibe = st.text_input(
#                 "Visual Style",
#                 value=st.session_state.form_data["style_pack"].get("vibe", "flat_illustration"),
#                 help="Enter your preferred visual style (see reference guide above)"
#             )
        
#         with col2:
#             aspect_ratio = st.text_input(
#                 "Aspect Ratio",
#                 value=st.session_state.form_data["style_pack"].get("aspect_ratio", "4:3"),
#                 help="Enter your preferred aspect ratio (see reference guide above)"
#             )
        
#         st.subheader("Additional Information")
        
#         additional_info = st.text_area(
#             "Additional Details",
#             value=st.session_state.form_data.get("additional_info", ""),
#             help="Specify any additional information such as characters, specific themes, cultural considerations, etc.",
#             height=120
#         )
        
#         col1, col2 = st.columns(2)
#         with col1:
#             submitted = st.form_submit_button("← Back to Audience", type="secondary")
#             if submitted:
#                 st.session_state.current_step = 3
#                 st.rerun()
        
#         with col2:
#             submitted = st.form_submit_button("Review & Continue →", type="primary")
#             if submitted:
#                 st.session_state.form_data["style_pack"] = {
#                     "palette": palette,
#                     "vibe": vibe,
#                     "aspect_ratio": aspect_ratio
#                 }
#                 st.session_state.form_data["additional_info"] = additional_info
#                 st.session_state.current_step = 5
#                 st.rerun()


def step_review_export():
    """Step 4: Review and Save Configuration"""
    st.markdown('<div class="step-header">📋 Review & Save Configuration</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-description">Review your information and save the configuration to continue with the workflow.</div>', unsafe_allow_html=True)
    
    # Display all collected information
    st.subheader("📚 Course Information")
    course_data = st.session_state.form_data["course"]
    st.markdown(f"**Course Title:** {course_data.get('course_title', 'Not provided')}")
    st.markdown(f"**Course Objectives:** {course_data.get('course_objectives', 'Not provided')}")
    
    st.subheader("🎯 Project Information")
    project_data = st.session_state.form_data["project"]
    st.markdown(f"**Module Title:** {project_data.get('module_title', 'Not provided')}")
    st.markdown(f"**Module Description:** {project_data.get('module_description', 'Not provided')}")
    st.markdown(f"**Project Title:** {project_data.get('project_title', 'Not provided')}")
    st.markdown(f"**Project Goal:** {project_data.get('project_goal', 'Not provided')}")
    st.markdown(f"**Project Learning Objectives:** {project_data.get('project_learning_objectives', 'Not provided')}")
    
    st.subheader("👥 Audience")
    audience_data = st.session_state.form_data["audience"]
    st.markdown(f"**Student Description:** {audience_data.get('student_description', 'Not provided')}")
    st.markdown(f"**Education Level:** {audience_data.get('education_level', 'Not provided')}")
    st.markdown(f"**Prerequisites:** {audience_data.get('prerequisites', 'Not provided')}")
    if audience_data.get('class_size'):
        st.markdown(f"**Class Size:** {audience_data.get('class_size')}")
    
    # Style preferences removed for now per updated workflow
    
    # Save and continue options
    st.subheader("💾 Save Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Audience", type="secondary"):
            st.session_state.current_step = 3
            st.rerun()
    
    with col2:
        if st.button("💾 Save & Continue", type="primary"):
            try:
                filepath = save_to_json()
                st.success(f"✅ Configuration saved successfully!")
                st.info(f"📁 Saved to: `{filepath}`")
                
                # Move to next step in workflow
                st.session_state.current_step = 5
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
    st.subheader("📄 Configuration Preview")
    st.json(st.session_state.form_data)


def step_next_phase():
    """Step 5: Next Phase - Scenario Generation"""
    st.markdown('<div class="step-header">🚀 Next Phase: Scenario Generation</div>', unsafe_allow_html=True)
    
    # Check if this is from existing module or newly saved
    if st.session_state.workflow_mode == "existing_module":
        st.markdown('<div class="step-description">Welcome back! You\'re continuing with an existing module. The next steps will involve generating scenario descriptions, image descriptions, and captions.</div>', unsafe_allow_html=True)
        
        # Show current course and module info
        course_title = st.session_state.selected_course
        module_title = st.session_state.selected_module
        
        st.info(f"📚 **Course:** {course_title}")
        st.info(f"🎯 **Module:** {module_title}")
        
        # Get the file path
        course_name = "".join(c for c in course_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
        module_name = "".join(c for c in module_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
        filepath = f"data/{course_name}/{module_name}/text_outputs/module_generation_information.json"
        
        st.info(f"📁 Configuration loaded from: `{filepath}`")
    else:
        st.markdown('<div class="step-description">Your configuration has been saved! The next steps will involve generating scenario descriptions, image descriptions, and captions.</div>', unsafe_allow_html=True)
        
        st.success("✅ Configuration saved successfully!")
        
        # Get the saved file path
        course_title = st.session_state.form_data["course"].get("course_title", "unknown_course")
        module_title = st.session_state.form_data["project"].get("module_title", "unknown_module")
        course_name = "".join(c for c in course_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
        module_name = "".join(c for c in module_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
        filepath = f"data/{course_name}/{module_name}/text_outputs/module_generation_information.json"
        
        st.info(f"📁 Configuration saved to: `{filepath}`")
    
    st.subheader("🎯 Next Steps in the Workflow")
    
    st.markdown("""
    The following steps will be performed automatically:
    
    1. **📝 Scenario Descriptions** - Generate detailed scenario descriptions based on your project goals
    2. **🖼️ Image Descriptions** - Create specific image descriptions for each scenario panel
    3. **💬 Caption Descriptions** - Generate caption text for each image
    4. **🎨 Image Generation** - Create the actual images using AI
    5. **📊 Final Assembly** - Compile everything into your motivation slides
    
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Start New Project", type="secondary"):
            st.session_state.current_step = 0
            st.session_state.workflow_mode = None
            st.session_state.form_data = get_default_form_data()
            st.rerun()
    
    with col2:
        if st.button("📋 View Configuration", type="primary"):
            st.session_state.current_step = 4
            st.rerun()
    
    # Add new button to start scenario generation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Scenario Generation", type="primary", use_container_width=True):
            st.session_state.current_step = 6
            st.session_state.scenarios_need_generation = True
            st.rerun()


def step_scenario_generation():
    """Step 6: Generate Scenario Description and Image Vibe"""
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
        
        # Display final scenario
        st.subheader("📝 Final Scenario")
        st.success(edited_scenario)
    
    # Navigation buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Next Phase", type="secondary"):
            st.session_state.current_step = 5
            st.rerun()
    
    with col2:
        if st.button("💾 Save & Continue", type="primary"):
            if selected_scenario is not None:
                try:
                    # Save scenario data
                    save_scenario_data(st.session_state.scenario_data, scenario_filepath)
                    st.success("✅ Scenario saved successfully!")
                    st.session_state.current_step = 5
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
