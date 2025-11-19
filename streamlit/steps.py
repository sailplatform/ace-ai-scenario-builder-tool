"""
Step functions for the AI Scenario Builder Tool workflow.
"""
import json
import os
import html
import base64
import io
from PIL import Image, ImageDraw, ImageFont
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


def _sanitize_name(value, fallback):
    cleaned = "".join(c for c in value if c.isalnum() or c in (" ", "-", "_")).rstrip().replace(" ", "_")
    return cleaned or fallback


def _clear_sidebar_keys():
    """Clear sidebar widget keys to force sync with updated data"""
    keys_to_clear = ["sidebar_scenario_edit", "sidebar_num_screens", "sidebar_aspect_ratio", 
                     "sidebar_visual_style", "sidebar_screen_0_caption", "sidebar_screen_0_img",
                     "modal_professional_domain", "modal_course_description", "modal_key_concept",
                     "modal_existing_challenge", "optional_additional_info"]
    for key in list(st.session_state.keys()):
        if key.startswith("sidebar_actor_") or key.startswith("sidebar_screen_") or key in keys_to_clear:
            del st.session_state[key]

def _get_text_output_dir():
    course_title = st.session_state.form_data["course"].get("course_title", "")
    module_title = st.session_state.form_data["project"].get("module_title", "")
    course_name = _sanitize_name(course_title, "course")
    module_name = _sanitize_name(module_title, "module")
    base_dir = os.path.join("data", course_name, module_name, "text_outputs")
    os.makedirs(base_dir, exist_ok=True)
    return base_dir


def _persist_generated_images():
    if "generated_images" not in st.session_state:
        return
    base_dir = _get_text_output_dir()
    filepath = os.path.join(base_dir, "generated_images.json")
    with open(filepath, "w") as f:
        json.dump(st.session_state.generated_images, f, indent=2)


def _save_composited_images(screens, images):
    """Save images with caption overlays to a folder"""
    base_dir = _get_text_output_dir()
    output_folder = os.path.join(base_dir, "composited_screens")
    os.makedirs(output_folder, exist_ok=True)
    
    for i, screen in enumerate(screens):
        if i < len(images) and images[i].get("image_b64"):
            try:
                image_b64 = images[i].get("image_b64", "")
                caption = screen.get("caption", "")
                
                img_data = base64.b64decode(image_b64)
                img = Image.open(io.BytesIO(img_data))
                draw = ImageDraw.Draw(img)
                
                if caption:
                    width, height = img.size
                    img_rgba = img.convert('RGBA')
                    temp_draw = ImageDraw.Draw(img_rgba)
                    
                    try:
                        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 20)
                    except:
                        try:
                            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
                        except:
                            try:
                                font = ImageFont.truetype("arial.ttf", 20)
                            except:
                                font = ImageFont.load_default()
                    
                    max_box_width = int(width * 0.9) - 48
                    words = caption.split()
                    lines = []
                    current_line = []
                    for word in words:
                        test_line = ' '.join(current_line + [word]) if current_line else word
                        bbox = temp_draw.textbbox((0, 0), test_line, font=font)
                        if bbox[2] - bbox[0] <= max_box_width:
                            current_line.append(word)
                        else:
                            if current_line:
                                lines.append(' '.join(current_line))
                            current_line = [word]
                    if current_line:
                        lines.append(' '.join(current_line))
                    
                    line_height = int(temp_draw.textbbox((0, 0), "A", font=font)[3] - temp_draw.textbbox((0, 0), "A", font=font)[1])
                    padding = 18
                    text_widths = [temp_draw.textbbox((0, 0), line, font=font)[2] - temp_draw.textbbox((0, 0), line, font=font)[0] for line in lines]
                    max_text_width = max(text_widths) if text_widths else 0
                    box_width = max_text_width + padding * 2
                    box_height = len(lines) * int(line_height * 1.4) + padding * 2
                    
                    box_left = (width - box_width) // 2
                    box_right = box_left + box_width
                    box_bottom = height - 24
                    box_top = box_bottom - box_height
                    radius = 14
                    
                    overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
                    overlay_draw = ImageDraw.Draw(overlay)
                    
                    overlay_draw.rounded_rectangle([box_left, box_top, box_right, box_bottom], 
                                                   radius=radius, fill=(255, 255, 255, 240), 
                                                   outline=(0, 0, 0, 30), width=1)
                    
                    img_rgba = Image.alpha_composite(img_rgba, overlay)
                    draw = ImageDraw.Draw(img_rgba)
                    
                    start_y = box_top + padding
                    for j, line in enumerate(lines):
                        bbox = draw.textbbox((0, 0), line, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_x = (width - text_width) // 2
                        text_y = start_y + j * int(line_height * 1.4)
                        draw.text((text_x, text_y), line, fill=(18, 18, 18), font=font)
                    
                    img = img_rgba.convert('RGB')
                
                output_path = os.path.join(output_folder, f"screen_{i+1}.png")
                img.save(output_path, "PNG")
            except Exception as e:
                st.error(f"Error saving screen {i+1}: {str(e)}")
    
    return output_folder


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
        course_description = form_data.get("course", {}).get("course_description", "")

        # Project/module information
        module_title = form_data.get("project", {}).get("module_title", "")
        key_concept = form_data.get("project", {}).get("key_concept", "")
        existing_challenge = form_data.get("project", {}).get("existing_challenge", "")

        # Audience information
        professional_domain = form_data.get("audience", {}).get("professional_domain", "")

        # General additional_info (not audience)
        additional_info = form_data.get("additional_info", "")
        
        # Extract existing scenario context if available
        existing_description = existing_scenario_data.get("scenario_description", "") if existing_scenario_data else ""
        
        # Create the prompt for GPT-4.1
        prompt = f"""
You are an expert instructional designer and learning experience designer who creates short, realistic, and motivating learning scenarios for higher education and professional audiences. Each scenario should connect the key concept to real-world practice, reflect the learners' context, and feel authentic to their field.

Using the information below, generate exactly 3 short scenario summaries (2–3 sentences each) that will help learners see the relevance and value of this concept or skill.
Inputs:
- Course: {course_title}
- Course Description: {course_description}
- Professional Domain: {professional_domain}
- Module Description: {module_title}
- Key Concept or Learning Objective: {key_concept}
- Learners' Existing Knowledge: {existing_challenge}
- Additional Information: {additional_info}

Your task:

Create 3 distinct scenario summaries that:
1. Are **realistic and relevant** to the learner profile and course context.
2. Clearly illustrate **how the key concept or skill applies in practice**.
3. Present a situation or challenge that encourages **critical thinking or decision-making**.
4. Use **authentic, inclusive examples** (diverse names, roles, and settings).
5. Specify a **clear setting or context** (e.g., workplace, community, field site, research team, or organizational meeting).
6. Feel **motivating and purposeful** — learners should understand why the skill or concept matters.

**Format your response as:**
SCENARIO 1: [summary with realistic context, diverse characters, and clear challenge]
SCENARIO 2: [summary with realistic context, diverse characters, and clear challenge]
SCENARIO 3: [summary with realistic context, diverse characters, and clear challenge]

**IMPORTANT: Each scenario must:**
- Write in plain, professional language suitable for higher education or adult learners.
- Keep tone **practical, motivational, and grounded in real-world settings**.
- Avoid jargon or overly academic phrasing.
- Focus on what’s happening and why it matters — not on lengthy backstories or character details.

Example response:
Course: Social Media Platforms
Learner Profile: Social Media Managers
Module Description: Content Moderation
Key Concept or Learning Objective: Understanding LLMs in content moderation
Learners’ Existing Knowledge: Basic understanding of content moderation
Additional Information: LLMs are becoming increasingly important in content moderation.

A suitable scenario summary could be:
safeChats is a fast-growing social media platform with active users worldwide. Their Trust and Safety team needs help strengthening content moderation systems and reducing costs. Currently, they use traditional sentiment analysis that flags posts as hate speech or not, but provides no explanations. Users complain about unfair flagging, and human reviewers spend extra time interpreting decisions. Their system also performs poorly in other languages. They're exploring Generative AI and LLMs because these can understand context, sarcasm, and nuance in multiple languages, explain reasoning in natural language, suggest better moderation responses, and continuously improve through feedback loops.
"""
        
        # Call GPT-4.1
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",  # GPT-4.1 model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that follows the provided task instructions carefully."},
                {"role": "user", "content": prompt},
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
    st.markdown('<div class="step-header">Choose how you\'d like to start your project</div>', unsafe_allow_html=True)
    # st.markdown('<div class="step-description">Choose how you\'d like to start your project.</div>', unsafe_allow_html=True)
    
    # Reset form data when returning to initial selection
    if st.session_state.workflow_mode is None or st.session_state.current_step == 0:
        st.session_state.form_data = get_default_form_data()
    
    # Check for existing courses
    existing_courses = get_existing_courses()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="step0-button">', unsafe_allow_html=True)
        if st.button("Create New Project", type="primary", use_container_width=True):
            st.session_state.workflow_mode = "new"
            st.session_state.form_data = get_default_form_data()
            st.session_state.current_step = 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="step0-button">', unsafe_allow_html=True)
        if existing_courses:
            if st.button("Use Existing Content", type="primary", use_container_width=True):
                st.session_state.workflow_mode = "existing"
                st.session_state.form_data = get_default_form_data()
                st.session_state.current_step = 0.5  # Special step for existing content selection
                st.rerun()
        else:
            st.markdown("No existing courses found.")
            st.button("Use Existing Content", disabled=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Show existing courses if any
    if existing_courses:
        st.markdown("---")
        st.subheader("📁 Existing Courses")
        st.markdown("Found the following existing courses:")
        
        for course in existing_courses:
            modules = get_existing_modules(course)
            with st.expander(f" {course} ({len(modules)} modules)"):
                if modules:
                    st.markdown("**Existing modules:**")
                    for module in modules:
                        st.markdown(f"  • {module}")
                else:
                    st.markdown("No modules found for this course.")


def step_existing_content_selection():
    """Step 0.5: Select existing course and module"""
    st.markdown('<div class="step-header">Select Existing Content</div>', unsafe_allow_html=True)
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

    st.markdown("""
    <style>
    /* Hide the search input inside the new Selectbox widget */
    .stSelectbox [data-baseweb="select"] input {
        opacity: 0 !important;         /* Hide text */
        height: 0 !important;          /* Collapse visible height */
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
    }</style>
    """, unsafe_allow_html=True)
    # Single key, no manual assignment after rendering
    st.selectbox(
        "Select Course",
        options=existing_courses,
        index=existing_courses.index(st.session_state.selected_course) if st.session_state.selected_course in existing_courses else 0,
        key="selected_course",
        on_change=_on_course_change,
        help="Choose an existing course to build upon",
        disabled=False
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
            base_path = os.path.join("data", course_name_clean, module_name_clean, "text_outputs")
            config_path = os.path.join(base_path, "context.json")

            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        existing_data = json.load(f)
                    st.session_state.form_data = existing_data
                    st.session_state.workflow_mode = "existing_module"
                    
                    # Detect last completed step based on files
                    scenario_desc_path = os.path.join(base_path, "scenario_descriptions.json")
                    metadata_path = os.path.join(base_path, "scenario_metadata.json")
                    screens_path = os.path.join(base_path, "screens.json")
                    images_path = os.path.join(base_path, "generated_images.json")
                    composited_path = os.path.join(base_path, "composited_screens")
                    
                    if os.path.exists(composited_path) and os.path.isdir(composited_path) and os.listdir(composited_path):
                        target_step = 7
                    elif os.path.exists(images_path):
                        target_step = 6
                    elif os.path.exists(screens_path):
                        target_step = 5
                    elif os.path.exists(metadata_path):
                        target_step = 4
                    elif os.path.exists(scenario_desc_path):
                        target_step = 3
                    else:
                        target_step = 2
                    
                    # Load existing data for the detected step
                    if target_step >= 3 and os.path.exists(scenario_desc_path):
                        with open(scenario_desc_path, 'r') as f:
                            scenario_data = json.load(f)
                            if "scenario_data" not in st.session_state:
                                st.session_state.scenario_data = {}
                            st.session_state.scenario_data["final_scenario"] = scenario_data.get("scenario_description", "")
                            st.session_state.scenarios_need_generation = False
                    
                    if target_step >= 4 and os.path.exists(metadata_path):
                        with open(metadata_path, 'r') as f:
                            st.session_state.metadata_data = json.load(f)
                            st.session_state.metadata_need_generation = False
                    
                    if target_step >= 5 and os.path.exists(screens_path):
                        with open(screens_path, 'r') as f:
                            st.session_state.screen_data = json.load(f)
                            st.session_state.screens_need_generation = False
                    
                    if target_step >= 6:
                        if os.path.exists(images_path):
                            with open(images_path, 'r') as f:
                                st.session_state.generated_images = json.load(f)
                        else:
                            st.session_state.generated_images = []
                    
                    st.session_state.current_step = target_step
                    _clear_sidebar_keys()
                    st.rerun()
                except Exception as e:
                    st.error(f" Could not load existing configuration: {str(e)}")
            else:
                st.error(" No existing configuration found for this module. Please create a new project instead.")

def step_project_setup():
    """Step 1: Combined Project Setup - All required information in one place"""
    st.markdown('<div class="step-header">Project Information</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="step-description">Let\'s set up your project with the essential information.</div>', unsafe_allow_html=True)
    
    with st.form("project_setup_form"):
        course_title = st.text_input(
            "What course or program is the scenario generation for?",
            value=st.session_state.form_data["course"].get("course_title", ""),
            help="So the scenario fits the subject and level of your learners.",
            placeholder="Enter the course or program name, e.g., Introduction to Data Analysis, Strategic Leadership"
        )
        
        professional_domain = st.text_input(
            "What is the learner's professional domain?",
            value=st.session_state.form_data["audience"].get("professional_domain", ""),
            help="This helps shape the tone and professional context of the scenario.",
            placeholder="e.g., Marketing professionals, Social media managers, Data analysts"
        )
        
        course_description = st.text_area(
            "What is a high-level course description?",
            value=st.session_state.form_data["course"].get("course_description", ""),
            help="Provide context about what the course covers overall.",
            placeholder="e.g., This course teaches students how to use AI tools for content moderation...",
            height=100
        )
        
        module_title = st.text_input(
            "Which topic or module should the scenario focus on?",
            value=st.session_state.form_data["project"].get("module_title", ""),
            help="So the scenario stays aligned with what learners are currently studying.",
            placeholder="Write the topic or module name, e.g., Ethical Decision-Making, Data Visualization"
        )
        
        key_concept = st.text_area(
            "What is the key concept or learning objective that the scenario should highlight?",
            value=st.session_state.form_data["project"].get("key_concept", ""),
            help="This becomes the main idea or concept the scenario brings to life.",
            placeholder="List one or two key ideas, e.g., analyzing information to make a decision",
            height=100
        )
        
        existing_challenge = st.text_area(
            "What do the learners already know about this topic?",
            value=st.session_state.form_data["project"].get("existing_challenge", ""),
            help="This helps set the right level of challenge.",
            placeholder="Mention what learners already understand, e.g., they know basic tools",
            height=100
        )
        
        submitted = st.form_submit_button("Continue to Review →", type="primary")
        
        if submitted:
            if all([course_title, professional_domain, course_description, module_title, key_concept, existing_challenge]):
                st.session_state.form_data["course"] = {
                    "course_title": course_title,
                    "course_description": course_description,
                    "course_objectives": st.session_state.form_data["course"].get("course_objectives", "")
                }
                st.session_state.form_data["project"] = {
                    "module_title": module_title,
                    "module_description": st.session_state.form_data["project"].get("module_description", ""),
                    "key_concept": key_concept,
                    "existing_challenge": existing_challenge,
                    "project_learning_objectives": st.session_state.form_data["project"].get("project_learning_objectives", "")
                }
                st.session_state.form_data["audience"] = {
                    "professional_domain": professional_domain,
                    "education_level": st.session_state.form_data["audience"].get("education_level", "undergrad_intro"),
                    "prerequisites": st.session_state.form_data["audience"].get("prerequisites", ""),
                    "class_size": st.session_state.form_data["audience"].get("class_size", 25)
                }
                # Clear modal widget keys to force them to sync with updated form_data
                _clear_sidebar_keys()
                st.session_state.current_step = 2
                st.rerun()
            else:
                st.error("Please fill in all required fields")

def step_review_export():
    """Step 2: Review and Save Configuration"""
    # Clear modal keys to ensure sidebar widgets sync with form_data
    _clear_sidebar_keys()
    
    st.markdown('<div class="step-header">Review & Save Configuration</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-description">Review your information and save the configuration. Next, you\'ll generate AI-powered scenario descriptions for your project.</div>', unsafe_allow_html=True)
    
    # Display all collected information
    st.subheader(" Course Information")
    course_data = st.session_state.form_data["course"]
    st.markdown(f"**Course/Program:** {course_data.get('course_title', 'Not provided')}")
    if course_data.get('course_objectives'):
        st.markdown(f"**Course Objectives:** {course_data.get('course_objectives', 'Not provided')}")
    
    st.subheader(" Module & Learning Information")
    project_data = st.session_state.form_data["project"]
    st.markdown(f"**Module/Topic:** {project_data.get('module_title', 'Not provided')}")
    if project_data.get('module_description'):
        st.markdown(f"**Module Description:** {project_data.get('module_description', 'Not provided')}")
    st.markdown(f"**Key Concept:** {project_data.get('key_concept', 'Not provided')}")
    st.markdown(f"**Existing Challenge:** {project_data.get('existing_challenge', 'Not provided')}")
    if project_data.get('project_learning_objectives'):
        st.markdown(f"**Learning Objectives:** {project_data.get('project_learning_objectives', 'Not provided')}")
    
    st.subheader("Audience")
    audience_data = st.session_state.form_data["audience"]
    st.markdown(f"**Professional Domain:** {audience_data.get('professional_domain', 'Not provided')}")
    
    st.subheader(" Course Description")
    st.markdown(f"**Description:** {course_data.get('course_description', 'Not provided')}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Project Information", type="secondary"):
            st.session_state.current_step = 1
            st.rerun()
    
    with col2:
        if st.button(" Save & Generate Scenarios", type="primary"):
            try:
                filepath = save_to_json()
                st.success(f" Configuration saved successfully!")
                st.info(f"📁 Saved to: `{filepath}`")
                
                # Move directly to scenario generation
                st.session_state.current_step = 3
                st.session_state.scenarios_need_generation = True
                st.rerun()
            except Exception as e:
                st.error(f" Error saving configuration: {str(e)}")
    
    with col3:
        if st.button(" Start Over", type="secondary"):
            st.session_state.current_step = 0
            st.session_state.workflow_mode = None
            st.session_state.form_data = get_default_form_data()
            st.rerun()
    
    # Display JSON preview
    # st.subheader("📄 Configuration Preview")
    # st.json(st.session_state.form_data)

def step_scenario_generation():
    """Step 3: Generate Scenario Description and Image Vibe"""
    # st.markdown('<div class="step-header">Scenario Generation</div>', unsafe_allow_html=True)
    # st.markdown('<div class="step-description">Generate three scenario options using AI and select the best one for your project.</div>', unsafe_allow_html=True)
    
    # Clear sidebar keys to ensure widgets sync with latest data
    _clear_sidebar_keys()
    
    # Check if scenario data already exists
    scenario_filepath = get_scenario_filepath(st.session_state.form_data)
    existing_scenario_data = load_scenario_data(scenario_filepath)
    
    # Check for existing scenario and offer to use it
    if existing_scenario_data and existing_scenario_data.get("final_scenario") and "scenarios_need_generation" not in st.session_state:
        st.info(" An existing scenario was found. Would you like to use it?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Use Existing Scenario", type="primary"):
                st.session_state.scenario_data = existing_scenario_data
                st.session_state.scenarios_need_generation = False
                _clear_sidebar_keys()
                st.rerun()
        with col2:
            if st.button("Generate New Scenario", type="secondary"):
                st.session_state.scenarios_need_generation = True
                st.rerun()
        st.markdown("---")
        st.subheader("Existing Scenario")
        st.info(existing_scenario_data.get("final_scenario", ""))
        return
    
    # Initialize scenario data if not exists
    if not hasattr(st.session_state, 'scenario_data') or not st.session_state.scenario_data:
        st.session_state.scenario_data = existing_scenario_data or {}
        if existing_scenario_data:
            _clear_sidebar_keys()
    
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
                _clear_sidebar_keys()
            except Exception as e:
                st.error(f" Error generating scenarios: {str(e)}")
                return
    
    # Display the three scenario options
    st.subheader(" Choose Your Scenario")
    st.markdown("Have three generated scenario options using AI and select the best one for your project. Then, edit it to better fit your needs:")
    
    scenarios = st.session_state.scenario_data.get("generated_scenarios", [])
    selected_scenario = st.session_state.scenario_data.get("selected_scenario", None)
    
    # Display scenarios in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # st.markdown("**Scenario Option 1**")
        if st.button("Select Option 1", key="select_1", type="primary" if selected_scenario == 0 else "secondary"):
            st.session_state.scenario_data["selected_scenario"] = 0
            st.rerun()
        st.info(scenarios[0] if len(scenarios) > 0 else "No scenario available")
    
    with col2:
        # st.markdown("**Scenario Option 2**")
        if st.button("Select Option 2", key="select_2", type="primary" if selected_scenario == 1 else "secondary"):
            st.session_state.scenario_data["selected_scenario"] = 1
            st.rerun()
        st.info(scenarios[1] if len(scenarios) > 1 else "No scenario available")
    
    with col3:
        # st.markdown("**Scenario Option 3**")
        if st.button("Select Option 3", key="select_3", type="primary" if selected_scenario == 2 else "secondary"):
            st.session_state.scenario_data["selected_scenario"] = 2
            st.rerun()
        st.info(scenarios[2] if len(scenarios) > 2 else "No scenario available")
    
    # Show selected scenario and allow editing
    if selected_scenario is not None:
        st.markdown("---")
        st.subheader(" Edit Your Selected Scenario")
        
        # Text area for editing the selected scenario
        scenario_text = scenarios[selected_scenario] if selected_scenario < len(scenarios) else ""
        approx_height = int(len(scenario_text) * 1.04) + 32  # just a bit bigger than text
        dynamic_height = min(max(130, approx_height), 240)   # cap reasonable max

        edited_scenario = st.text_area(
            "Edit your scenario directly:",
            value=scenario_text,
            height=dynamic_height,
            key="edit_scenario"
        )
        
        # Update the scenario data
        if edited_scenario != scenarios[selected_scenario]:
            st.session_state.scenario_data["generated_scenarios"][selected_scenario] = edited_scenario
            st.session_state.scenario_data["final_scenario"] = edited_scenario
            _clear_sidebar_keys()
        
        # LLM-based editing
        update_instructions = st.text_area(
            "Or use AI to refine your scenario. Describe how you'd like to modify the scenario:",
            placeholder="e.g., Make it more technical, add more diversity, focus on practical applications",
            height=80,
            key="llm_update_instructions"
        )
        
        if st.button("Update with AI", type="secondary"):
            if update_instructions:
                with st.spinner("🤖 Updating scenario with AI..."):
                    try:  
                        course_title = st.session_state.form_data["course"].get("course_title", "")
                        course_description = st.session_state.form_data["course"].get("course_description", "")
                        professional_domain = st.session_state.form_data["audience"].get("professional_domain", "")
                        module_title = st.session_state.form_data["project"].get("module_title", "")
                        key_concept = st.session_state.form_data["project"].get("key_concept", "")
                        existing_challenge = st.session_state.form_data["project"].get("existing_challenge", "")
                        additional_info = st.session_state.form_data.get("additional_info", "")
                        prompt = f"""
You are an expert instructional designer and learning experience designer who creates short, realistic, and motivating learning scenarios for higher education and professional audiences. Each scenario should connect the key concept to real-world practice, reflect the learners' context, and feel authentic to their field.

Based on the following inputs, update the current scenario according to the update instructions:
Current scenario: {edited_scenario}
Update instructions: {update_instructions}

Inputs:
- Course: {course_title}
- Course Description: {course_description}
- Professional Domain: {professional_domain}
- Module Description: {module_title}
- Key Concept or Learning Objective: {key_concept}
- Learners' Existing Knowledge: {existing_challenge}
- Additional Information: {additional_info}

Scenarios should
1. Be **realistic and relevant** to the learner profile and course context.
2. Clearly illustrate **how the key concept or skill applies in practice**.
3. Present a situation or challenge that encourages **critical thinking or decision-making**.
4. Use **authentic, inclusive examples** (diverse names, roles, and settings).
5. Specify a **clear setting or context** (e.g., workplace, community, field site, research team, or organizational meeting).
6. Feel **motivating and purposeful** — learners should understand why the skill or concept matters.
7. Be 2-3 sentences long. Do not add any other text or formatting.

**IMPORTANT: Each scenario must:**
- Write in plain, professional language suitable for higher education or adult learners.
- Keep tone **practical, motivational, and grounded in real-world settings**.
- Avoid jargon or overly academic phrasing.
- Focus on what’s happening and why it matters — not on lengthy backstories or character details.

**CRITICAL:** Your response must contain ONLY the scenario text. No prefixes, no labels, no metadata, no explanations - just the scenario itself.

Example of correct format:
safeChats is a fast-growing social media platform with active users worldwide. Their Trust and Safety team needs help strengthening content moderation systems and reducing costs. Currently, they use traditional sentiment analysis that flags posts as hate speech or not, but provides no explanations. Users complain about unfair flagging, and human reviewers spend extra time interpreting decisions. Their system also performs poorly in other languages. They're exploring Generative AI and LLMs because these can understand context, sarcasm, and nuance in multiple languages, explain reasoning in natural language, suggest better moderation responses, and continuously improve through feedback loops.
"""
                        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                        response = client.chat.completions.create(
                            model="gpt-4-1106-preview",  # GPT-4.1 model
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant that follows the provided task instructions carefully."},
                                {"role": "user", "content": prompt},
                            ],
                            max_tokens=800,
                            temperature=0.7
                        )
                        updated_scenario = response.choices[0].message.content.strip()
                        st.session_state.scenario_data["generated_scenarios"][selected_scenario] = updated_scenario
                        st.session_state.scenario_data["final_scenario"] = updated_scenario
                        if "edit_scenario" in st.session_state:
                            del st.session_state["edit_scenario"]
                        _clear_sidebar_keys()
                        st.success(" Scenario updated with AI!")
                        st.rerun()
                    except Exception as e:
                        st.error(f" Error updating scenario: {str(e)}")
            else:
                st.error("Please provide update instructions.")
        
        # Display final scenario
        st.subheader(" Final Scenario")
        final_scenario_display = st.session_state.scenario_data.get("final_scenario", edited_scenario)
        st.success(final_scenario_display)
    
    # Navigation buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Review", type="secondary"):
            st.session_state.current_step = 2
            st.rerun()
    
    with col2:
        if st.button(" Save & Continue", type="primary"):
            if selected_scenario is not None:
                try:
                    # Save scenario data
                    st.session_state.scenario_data["final_scenario"] = edited_scenario
                    _clear_sidebar_keys()
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
                    
                    st.success(" Scenario saved successfully!")
                    st.session_state.current_step = 4
                    st.session_state.metadata_need_generation = True
                    st.rerun()
                except Exception as e:
                    st.error(f" Error saving scenario data: {str(e)}")
            else:
                st.error("Please select a scenario before saving.")
    
    with col3:
        if st.button(" Generate New Options", type="secondary"):
            # Clear existing scenarios and regenerate
            if "scenario_data" in st.session_state:
                st.session_state.scenario_data.pop("generated_scenarios", None)
                st.session_state.scenario_data.pop("selected_scenario", None)
                st.session_state.scenario_data.pop("final_scenario", None)
            st.session_state.scenarios_need_generation = True
            st.rerun()


def step_scenario_metadata():
    """Step 4: Generate Scenario Metadata and Actors"""
    # Clear sidebar keys to ensure widgets sync with latest data
    _clear_sidebar_keys()
    
    st.markdown('<div class="step-header">Scenario Metadata & Actors</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-description">Generate metadata and actors for your scenario using AI.</div>', unsafe_allow_html=True)
    
    # Initialize metadata generation flag
    if "metadata_need_generation" not in st.session_state:
        st.session_state.metadata_need_generation = True
    
    # Get final scenario
    final_scenario = st.session_state.scenario_data.get("final_scenario", "")
    
    # Check for existing metadata
    course_title = st.session_state.form_data["course"].get("course_title", "")
    module_title = st.session_state.form_data["project"].get("module_title", "")
    course_name = "".join(c for c in course_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
    module_name = "".join(c for c in module_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
    metadata_filepath = f"data/{course_name}/{module_name}/text_outputs/scenario_metadata.json"
    
    existing_metadata = None
    if os.path.exists(metadata_filepath):
        try:
            with open(metadata_filepath, 'r') as f:
                existing_metadata = json.load(f)
        except:
            pass
    
    # Initialize metadata data if not exists
    if "metadata_data" not in st.session_state or not st.session_state.metadata_data:
        st.session_state.metadata_data = existing_metadata or {}
        if existing_metadata:
            _clear_sidebar_keys()
    
    # Offer to use existing metadata
    if existing_metadata and existing_metadata.get("actors") and "metadata_need_generation" not in st.session_state:
        st.info(" Existing metadata and actors were found. Would you like to use them?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Use Existing Metadata", type="primary"):
                st.session_state.metadata_data = existing_metadata
                st.session_state.metadata_need_generation = False
                _clear_sidebar_keys()
                st.rerun()
        with col2:
            if st.button("Generate New Metadata", type="secondary"):
                st.session_state.metadata_need_generation = True
                st.rerun()
        st.markdown("---")
        st.subheader("Existing Metadata")
        st.json(existing_metadata)
        return

    # Generate metadata when flag is True
    if st.session_state.metadata_need_generation:
        with st.spinner("Generating scenario metadata with AI..."):
            try:
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                
                prompt = f"""You are an instructional scenario designer. Based on the scenario description, extract key visual and narrative metadata.

Scenario: {final_scenario}

Course: {st.session_state.form_data["course"].get("course_title", "")}
Module: {st.session_state.form_data["project"].get("module_title", "")}

Your task:
1. Determine how many visual screens are needed to convey the scenario effectively (usually between 3 and 7).
2. Recommend the most suitable aspect ratio for these screens (e.g., 16:9, 9:16, 1:1) based on the learning context.
3. Identify the main character:
   - Include name, role or title, and a clear explanation of their *objective* and *decision-making context* in the scenario.
4. Identify any side or supporting characters (only if they contribute meaningfully to the scenario's progression). There should be either 0 or 1 supporting character:
   - Include name, role or title, and a concise explanation of how they *interact with or influence the main character's goal*.
5. For each character, provide a brief visual appearance description to ensure visual consistency across images. IMPORTANT: Characters should be diverse in terms of ethnicity, gender, age, and other characteristics. Avoid stereotypes and ensure representation reflects real-world diversity.
 
Output strictly in JSON format:
{{
  "num_screens": <integer>,
  "aspect_ratio": "<string>",
  "actors": [
    {{
      "name": "<string>",
      "role": "<string>",
      "purpose": "<describe what they are trying to accomplish and how their actions or perspective drive the scenario forward>",
      "appearance": "<brief visual description including age, ethnicity, gender, and distinctive features. Ensure diversity>"
    }},
    {{
      "name": "<string>",
      "role": "<string>",
      "purpose": "<describe how this supporting character enables, challenges, or informs the main character's decisions>",
      "appearance": "<brief visual description including age, ethnicity, gender, and distinctive features. Ensure diversity>"
    }}
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
                    _clear_sidebar_keys()
                else:
                    st.error("Failed to parse metadata")
            except Exception as e:
                st.error(f" Error generating metadata: {str(e)}")
                return
    
    # Display and edit actors
    st.subheader("Actors")
    
    actors = st.session_state.metadata_data.get("actors", [])
    if not actors:
        actors = [{"name": "", "role": "", "purpose": "", "appearance": ""}]
    
    edited_actors = []
    to_delete = None

    for i, actor in enumerate(actors):
        with st.expander(f"Actor {i+1}: {actor.get('name', 'New Actor')}", expanded=True):
            cols = st.columns([10, 1.4])
            with cols[0]:
                name = st.text_input("Name", value=actor.get("name", ""), key=f"actor_{i}_name")
                role = st.text_input("Role", value=actor.get("role", ""), key=f"actor_{i}_role")
                purpose_text = actor.get("purpose", "")
                appearance_text = actor.get("appearance", "")
                # Dynamically calculate height based on length of text (minimum 80, max 400 for large entries)
                purpose_height = min(max(80, int(len(purpose_text) * 1.2) + 40), 125)
                appearance_height = min(max(80, int(len(appearance_text) * 1.2) + 40), 125)
                purpose = st.text_area(
                    "Character's Objective",
                    value=purpose_text,
                    key=f"actor_{i}_purpose",
                    height=purpose_height
                )
                appearance = st.text_area("Visual Appearance", value=appearance_text, key=f"actor_{i}_appearance", height=appearance_height, help="Describe appearance including age, ethnicity, gender, distinctive features. Ensure diversity.")
            with cols[1]:
                if st.button("Delete", key=f"delete_actor_{i}"):
                    to_delete = i
            
            edited_actors.append({
                "name": name,
                "role": role,
                "purpose": purpose,
                "appearance": appearance
            })
    
    if to_delete is not None:
        actors.pop(to_delete)
        st.session_state.metadata_data["actors"] = actors
        st.rerun()

    if st.button("Add Actor"):
        actors.append({"name": "", "role": "", "purpose": "", "appearance": ""})
        st.session_state.metadata_data["actors"] = actors
        st.rerun()
    
    st.session_state.metadata_data["actors"] = edited_actors

    
    # Display and edit metadata
    st.markdown("---")
    st.subheader("Scenario Metadata")
    
    num_screens = st.number_input(
        "Number of Screens",
        min_value=1,
        max_value=20,
        value=st.session_state.metadata_data.get("num_screens", 5),
        key="edit_num_screens"
    )
    
    aspect_ratio = st.text_input(
        "Aspect Ratio",
        value=st.session_state.metadata_data.get("aspect_ratio", "16:9"),
        key="edit_aspect_ratio"
    )
    
    visual_style = st.text_input(
        "Visual Style",
        value="A vibrant, semi-realistic digital illustration in a modern vector art style, with soft gradients, clean lines, and cinematic lighting.",
        key="edit_visual_style"
    )
    
    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Scenario", type="secondary"):
            st.session_state.current_step = 3
            st.rerun()
    
    with col2:
        if st.button("Save & Continue", type="primary"):
            try:
                # Update metadata
                st.session_state.metadata_data.update({
                    "num_screens": num_screens,
                    "aspect_ratio": aspect_ratio,
                    "visual_style": visual_style,
                    "actors": edited_actors
                })
                _clear_sidebar_keys()
                
                # Save to file
                course_title = st.session_state.form_data["course"].get("course_title", "")
                module_title = st.session_state.form_data["project"].get("module_title", "")
                course_name = "".join(c for c in course_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
                module_name = "".join(c for c in module_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
                metadata_filepath = f"data/{course_name}/{module_name}/text_outputs/scenario_metadata.json"
                os.makedirs(os.path.dirname(metadata_filepath), exist_ok=True)
                with open(metadata_filepath, 'w') as f:
                    json.dump(st.session_state.metadata_data, f, indent=2)
                
                st.success("Metadata saved successfully!")
                st.session_state.current_step = 5
                st.session_state.screens_need_generation = True
                st.rerun()
            except Exception as e:
                st.error(f"Error saving metadata: {str(e)}")
    
    with col3:
        if st.button("Regenerate", type="secondary"):
            st.session_state.metadata_need_generation = True
            st.rerun()


def step_screen_generation():
    """Step 5: Generate Screens with Image Descriptions and Captions"""
    # Clear sidebar keys to ensure widgets sync with latest data
    _clear_sidebar_keys()
    
    st.markdown('<div class="step-header">Screen Generation</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-description">Generate screens with image descriptions and captions for your scenario.</div>', unsafe_allow_html=True)
    
    # Get necessary data for file paths
    course_title = st.session_state.form_data["course"].get("course_title", "")
    module_title = st.session_state.form_data["project"].get("module_title", "")
    course_name = "".join(c for c in course_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
    module_name = "".join(c for c in module_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
    screens_filepath = f"data/{course_name}/{module_name}/text_outputs/screens.json"
    
    # Check for existing screen data
    existing_screen_data = None
    if os.path.exists(screens_filepath):
        try:
            with open(screens_filepath, 'r') as f:
                existing_screen_data = json.load(f)
        except:
            pass
    
    # Initialize screen generation flag
    if "screens_need_generation" not in st.session_state:
        st.session_state.screens_need_generation = True
    
    # Initialize screen data if not exists
    if "screen_data" not in st.session_state or not st.session_state.screen_data:
        st.session_state.screen_data = existing_screen_data or {}
        if existing_screen_data:
            _clear_sidebar_keys()
    
    # Get necessary data
    final_scenario = st.session_state.scenario_data.get("final_scenario", "")
    num_screens = st.session_state.metadata_data.get("num_screens", 5)
    actors = st.session_state.metadata_data.get("actors", [])
    
    # Generate screens when flag is True
    if st.session_state.screens_need_generation:
        with st.spinner("🤖 Generating screens with AI..."):
            try:
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                
                actors_str = "\n".join([f"- {a['name']} ({a['role']}): {a['purpose']}" for a in actors])
                key_concept = st.session_state.form_data["project"].get("key_concept", "")
                
                prompt = f"""
You are an expert instructional designer and learning experience designer who creates short, realistic, and motivating learning scenarios for higher education and professional audiences. Each scenario should connect the key concept to real-world practice, reflect the learners' context, and feel authentic to their field.                

**Goal:** Create {num_screens} sequential screens that visually tell the story described below. The PRIMARY focus should be on clearly depicting and reinforcing the learning objective: {key_concept}. Each screen should directly connect to how this concept is applied, learned, or demonstrated in the scenario.

**Story Arc:**  
Follow the traditional story structure of:
1. **Beginning** – Introduce the context, characters, and the inciting incident that sets the story in motion.  
2. **Rising Action** – Build tension or challenge as the main event or conflict unfolds.  
3. **Climax** – Present the turning point or key decision moment.  
4. **Falling Action** – Show the outcome or consequence of that moment.  
5. **Resolution** – End with an insight, learning, or call to action that ties back to the learning goal.

**Scenario:**  
{final_scenario}

**Actors:**  
{actors_str}

**Course:** {st.session_state.form_data["course"].get("course_title", "")}  
**Module:** {st.session_state.form_data["project"].get("module_title", "")}

**Guidelines:**
1. Each screen should advance the story in a logical and emotionally engaging way, aligned with the storytelling arc above.  
2. Write **image_description** as if it will be sent directly to a generative image model. Use vivid, cinematic visual language that describes:
   - The setting, mood, and lighting  
   - Character expressions, gestures, and positions  
   - Relevant props, backgrounds, and atmosphere  
3. Avoid elements that generative AI renders poorly:
   - No text, labels, symbols, or charts  
   - No diagrams, models, mockups, graphs, or technical visualizations
   - No complex abstractions (e.g., metaphors, irony, conceptual visuals)
   - Focus ONLY on scenes, people, environments, and objects that can be realistically photographed or illustrated
   - Instead of mentioning character names, the focus on image generation is more on the character visual.
4. Write **caption** as a short motivational or descriptive text that connects the visual to the story and learning objective.  
   - Keep captions natural, concise, and meaningful.  

**Learning Objective Focus:**
- Each screen should prioritize showing the learning objective in action, not just character interactions.
- Focus on the conceptual understanding, problem-solving, or skill demonstration related to: {key_concept}
- Character interactions should serve to illustrate the learning objective, not be the main focus.

**Storytelling Best Practices:**
- Maintain tone consistency across all screens (same mood, pacing, and style).
- Use human-centered details (body language, environment, emotion) to make the story relatable.  
- End with insight or resolution that ties directly back to the learning objective.

Format as JSON:
{{
  "screens": [
    {{"screen_number": 1, "image_description": "", "caption": ""}},
    {{"screen_number": 2, "image_description": "", "caption": ""}}
  ]
}}

Example response:
Scenario: safeChats is a fast-growing social media platform, having active users everyday around the world and users posts in multiple languages. The Trust and Safety team of safeChats wants to strengthen their content moderation system and reduce moderation costs. Currently, they use traditional sentiment analysis that flags posts as hate speech or not hate speech. Users complain about unfair flagging, and human reviewers spend extra time interpreting decisions. Their system also performs poorly in other languages. They're exploring Generative AI and LLMs because these can understand context, sarcasm, and nuance in multiple languages, explain reasoning in natural language, suggest better moderation responses, and continuously improve through feedback loops.
Actors: No actors are needed for this scenario.

A suitable response could be:
"screens": [
    {{
      "screen_number": 1,
      "image_description": "A dynamic split-screen showing a young user sitting at a café posting on safeChats from their phone, with the background illustrating global connectivity through soft glowing world map lines. On the other side, a diverse team of content moderators works in a bright office, reviewing posts on their monitors. The mood is active and global, rendered in a clean flat-vector style with warm blues and yellows.",
      "caption": "safeChats is a fast-growing social media platform, having active users everyday around the world and users posts in multiple languages. The Trust and Safety team of safeChats wants to strengthen their content moderation system and reduce moderation costs."
    }},
    {{
      "screen_number": 2,
      "image_description": "A computer dashboard interface displaying flagged posts with only two labels visible: 'hate speech' or 'not hate speech'. The moderators observe the screen, appearing slightly puzzled by the lack of context. The visuals emphasize simplicity and monotony, showing uniform posts on the dashboard. The scene is illustrated in a cool-toned flat style to highlight technological limitation.",
      "caption": "safeChats currently uses a traditional sentiment analysis model that flags posts as either hate speech or not hate speech."
    }},
    {{
      "screen_number": 3,
      "image_description": "Inside the moderation center, a content moderator reviews posts written in multiple languages on multiple monitors. The moderator takes handwritten notes and highlights unclear posts with sticky notes while frowning in concentration. The lighting is dimmer, symbolizing effort and cognitive load. The visual style remains flat and professional, using muted greys and blues.",
      "caption": "While this approach helps identify harmful content in English, moderators face a serious challenge — the system provides no explanation for its decisions and cannot support the growing marketplace of the platform in multiple countries."
    }},
    {{
      "screen_number": 4,
      "image_description": "Three moderators sit together at a long desk filled with screens showing flagged posts. One moderator leans back, another rubs their forehead, and a third scrolls through endless messages. The atmosphere is tense and slightly fatigued, with soft overhead lighting. The visual emphasizes the emotional burden of unclear decisions in a realistic office setting.",
      "caption": "Without clear reasoning and multi-language support, human reviewers must spend extra time interpreting why a post was flagged and determining whether the classification was fair or contextually accurate."
    }},
    {{
      "screen_number": 5,
      "image_description": "A conference room scene featuring the Head of Content Moderation, AI engineers, and senior leaders gathered around a digital whiteboard showing conceptual AI architecture. Laptops and holographic visuals are on the table. The lighting is bright and forward-looking, symbolizing innovation. The color palette includes optimistic shades of teal and gold.",
      "caption": "To improve both speed and transparency, safeChats is exploring the potential of Generative AI (GenAI) and Large Language Models (LLMs)."
    }},
    {{
      "screen_number": 6,
      "image_description": "A side-by-side comparison of two digital interfaces: on the left, a basic model incorrectly flags a post for containing the word 'destroyed'; on the right, a modern AI interface shows contextual understanding, displaying a visual of balanced speech bubbles and multilingual cues. The scene conveys accuracy and intelligence, using clean, illustrative graphics without text or labels.",
      "caption": "Unlike standard classifiers, LLMs can understand context, sarcasm, and nuance in multiple languages, explain their reasoning in natural language, and suggest better moderation responses such as rephrasing or issuing a warning."
    }},
    {{
      "screen_number": 7,
      "image_description": "A bright office with moderators smiling as they interact with a transparent, AI-assisted moderation dashboard. The central screen displays visuals of global communication and safety icons. The environment feels calm and empowered, with green and light blue hues symbolizing trust and progress.",
      "caption": "By leveraging feedback loops and fine-tuning, safeChats aims to build a smarter, more transparent moderation system — one that empowers human moderators and keeps online conversations safe."
    }}
  ]
"""
                
                response = client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=[
                        {"role": "system", "content": "You are an expert instructional designer and learning experience designer who creates short, realistic, and motivating learning scenarios for higher education and professional audiences. Each scenario should connect the key concept to real-world practice, reflect the learners' context, and feel authentic to their field. Generate screen content in valid JSON format."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7
                )
                
                import re
                content = response.choices[0].message.content
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    screen_data = json.loads(json_match.group())
                    st.session_state.screen_data = screen_data
                    st.session_state.screens_need_generation = False
                    _clear_sidebar_keys()
                else:
                    st.error("Failed to parse screen data")
            except Exception as e:
                st.error(f"Error generating screens: {str(e)}")
                return
    
    # Display and edit screens
    screens = st.session_state.screen_data.get("screens", [])
    
    for i, screen in enumerate(screens):
        with st.expander(f"Screen {i+1}", expanded=True):
            caption = st.text_area(f"Caption", value=screen.get("caption", ""), key=f"screen_{i}_caption", height=80)
            image_desc = st.text_area(f"Image Description", value=screen.get("image_description", ""), key=f"screen_{i}_img", height=100)
            screens[i]["caption"] = caption
            screens[i]["image_description"] = image_desc
    
    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Metadata", type="secondary"):
            st.session_state.current_step = 4
            st.rerun()
    
    with col2:
        if st.button("Save & Generate Images", type="primary"):
            try:
                # Save to file
                course_title = st.session_state.form_data["course"].get("course_title", "")
                module_title = st.session_state.form_data["project"].get("module_title", "")
                course_name = "".join(c for c in course_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
                module_name = "".join(c for c in module_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
                screens_filepath = f"data/{course_name}/{module_name}/text_outputs/screens.json"
                os.makedirs(os.path.dirname(screens_filepath), exist_ok=True)
                with open(screens_filepath, 'w') as f:
                    json.dump(st.session_state.screen_data, f, indent=2)
                
                _clear_sidebar_keys()
                st.success("Screens saved successfully!")
                st.session_state.current_step = 6
                st.rerun()
            except Exception as e:
                st.error(f"Error saving screens: {str(e)}")
    
    with col3:
        if st.button("Regenerate", type="secondary"):
            st.session_state.screens_need_generation = True
            st.rerun()


def step_image_generation():
    """Step 6: Generate Images for Each Screen"""
    screens = st.session_state.screen_data.get("screens", [])
    generated_images = st.session_state.get("generated_images", [])
    images_ready = (
        screens
        and len(generated_images) >= len(screens)
        and all(
            generated_images[i].get("image_b64")
            for i in range(len(screens))
        )
    )
    if images_ready:
        if st.button("Preview Final Slideshow", key="go_to_preview", type="primary"):
            st.session_state.preview_index = 0
            st.session_state.should_save_composited = True
            st.session_state.current_step = 7
            st.rerun()

    # Initialize image generation
    if "current_image_index" not in st.session_state:
        st.session_state.current_image_index = 0
    
    if "generated_images" not in st.session_state:
        st.session_state.generated_images = []
    
    if not screens:
        st.error("No screens found. Please go back and generate screens first.")
        if st.button("← Back to Screens"):
            st.session_state.current_step = 5
            st.rerun()
        return
    
    current_idx = st.session_state.current_image_index
    if current_idx >= len(screens):
        st.success("All images generated successfully!")
        st.info(f"You've completed generating {len(screens)} images for your scenario.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Screens", type="secondary"):
                st.session_state.current_step = 5
                st.rerun()
        with col2:
            if st.button("Start Over", type="primary"):
                st.session_state.current_image_index = 0
                st.session_state.generated_images = []
                st.rerun()
        return
    
    current_screen = screens[current_idx]
    
    # Navigation section - jump to any screen
    st.subheader("Navigation")
    nav_cols = st.columns([0.5, 1])
    with nav_cols[0]:
        all_screen_options = list(range(len(screens)))
        # To prevent typing, use st.radio (no free entry, just options)
        selected_screen = st.radio(
            "Jump to Screen",
            options=all_screen_options,
            format_func=lambda x: f"Screen {x + 1}" + (" (Generated)" if x < len(st.session_state.generated_images) and st.session_state.generated_images[x].get("image_b64") else " (Not Generated)"),
            index=current_idx,
            key="nav_radio_screen"
        )
        if selected_screen != current_idx:
            st.session_state.current_image_index = selected_screen
            st.rerun()
        st.caption(f"Current: Screen {current_idx + 1} of {len(screens)}")
    with nav_cols[1]:
        with st.expander("Tips for Editing Image Prompts", expanded=False):
            st.markdown(
                """
                <style>

                /* Make entire expander border teal */
                details {
                    # border: 2px solid #00847F !important;
                    border-radius: 6px !important;
                    overflow: hidden;
                }

                /* Style the expander header bar */
                details > summary {
                    # background-color: #00847F !important;
                    # color: white !important;
                    # padding: 0.75rem !important;
                    font-weight: 600 !important;
                    list-style: none !important;
                }

                </style>
                """,
                unsafe_allow_html=True
            )

            st.markdown("""
            **Make characters feel real**

            Include a mix of ages, genders, and ethnicities.

            Describe people naturally and avoid stereotypes.

            **Keep the visuals clear**

            Mention lighting, mood, and the setting so the scene is easy to picture.

            Avoid including text in images.

            **Add useful context**

            Describe where the scene takes place and what's happening.

            Include relevant objects or details that support the learning goal.

            **Avoid abstract ideas**

            Stay away from metaphors or concepts that are difficult for AI to render literally.
            """)

    
    st.markdown("---")
    st.subheader(f"Screen {current_idx + 1} of {len(screens)}")
    
    # Allow editing before generation
    edited_caption = st.text_area(
        "Caption",
        value=current_screen.get("caption", ""),
        key=f"edit_caption_{current_idx}",
        height=80
    )
    
    edited_image_desc = st.text_area(
        "Image Description",
        value=current_screen.get("image_description", ""),
        key=f"edit_img_desc_{current_idx}",
        height=150
    )
    
    screens[current_idx]["caption"] = edited_caption
    screens[current_idx]["image_description"] = edited_image_desc
    
    # Check if regeneration is needed
    needs_generation = current_idx >= len(st.session_state.generated_images) or not st.session_state.generated_images[current_idx].get("image_b64")
    
    # Auto-regenerate if flag is set
    auto_regenerate = st.session_state.get("regenerate_image") == current_idx
    if auto_regenerate:
        needs_generation = True
        st.session_state.regenerate_image = None
    
    # Generate image if not already generated for this screen
    if needs_generation:
        if auto_regenerate:
            # Auto-generate on rerun after regenerate button clicked
            pass
        elif not st.button("Generate Image", type="primary", use_container_width=True):
            return
        
        # Generate the image
        if True:
            with st.spinner(f"🤖 Generating image {current_idx + 1} of {len(screens)}..."):
                try:
                    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                    
                    visual_style = st.session_state.metadata_data.get("visual_style", "A vibrant, semi-realistic digital illustration in a modern vector art style, with soft gradients, clean lines, and cinematic lighting.")
                    aspect_ratio = st.session_state.metadata_data.get("aspect_ratio", "16:9")
                    
                    actors = st.session_state.metadata_data.get("actors", [])
                    actor_appearances = [f"{a.get('name', '')}: {a.get('appearance', '')}" for a in actors if a.get("appearance")]
                    actor_context = f" Character appearances for consistency: {'. '.join(actor_appearances)}." if actor_appearances else ""
                    
                    # Include previous screen context for consistency
                    prev_context = ""
                    if current_idx > 0:
                        prev_screen = screens[current_idx - 1]
                        prev_desc = prev_screen.get("image_description", "")
                        if prev_desc:
                            prev_context = f" Previous screen context for visual consistency: {prev_desc}. "
                    
                    image_prompt = f"{edited_image_desc}{prev_context}{actor_context} Style: {visual_style}. Aspect ratio: {aspect_ratio}."
                    
                    response = client.images.generate(
                        model="gpt-image-1-mini",
                        prompt=image_prompt,
                        size=(
                            "1024x1024" if aspect_ratio == "1:1" 
                            else "1536x1024" if aspect_ratio == "16:9" 
                            else "1024x1536"
                        ),
                    )

                    # gpt-image-1-mini returns base64 in b64_json
                    image_b64 = response.data[0].b64_json

                    # Ensure the index exists inside the session list
                    if current_idx >= len(st.session_state.generated_images):
                        st.session_state.generated_images.extend(
                            [{}] * (current_idx - len(st.session_state.generated_images) + 1)
                        )

                    # Store image metadata
                    st.session_state.generated_images[current_idx] = {
                        "image_b64": image_b64,
                        "accepted": False,
                        "screen_number": current_idx + 1
                    }

                    _persist_generated_images()
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating image: {str(e)}")
                    return
    
    # Display current screen image
    # st.markdown("---")
    # st.subheader("Current Generated Image")
    # if current_idx < len(st.session_state.generated_images) and st.session_state.generated_images[current_idx].get("image_url"):
    #     current_image = st.session_state.generated_images[current_idx]
    #     st.image(current_image["image_url"], width=360)
    # else:
    #     st.info("Generate this screen's image to preview it here.")

    all_generated = [(i, img) for i, img in enumerate(st.session_state.generated_images) if img.get("image_b64")]
    if all_generated:
        st.markdown("---")
        st.subheader("All Generated Screens")
        num_per_row = 2

        for row_start in range(0, len(all_generated), num_per_row):
            row_items = all_generated[row_start:row_start + num_per_row]
            cols = st.columns(2, gap="small")

            for idx, (orig_idx, img_data) in enumerate(row_items):
                with cols[idx]:
                    is_current = orig_idx == current_idx
                    caption_text = screens[orig_idx].get("caption", "") if orig_idx < len(screens) else ""
                    image_data_uri = f"data:image/png;base64,{img_data['image_b64']}"
                    
                    img_style = "display:block; width:100%; height:auto; border-radius:18px; object-fit:cover;"
                    if not is_current:
                        img_style += " filter:grayscale(65%) contrast(95%); opacity:0.75;"

                    st.markdown(
                        f"""
                        <div style="position:relative; width:100%; margin-bottom:1rem;">
                            <img src="{image_data_uri}" style="{img_style}">
                            {f'<div style="position:absolute; left:12px; right:12px; bottom:12px; background:rgba(255,255,255,0.94); border-radius:8px; padding:8px 12px; box-shadow:0 4px 12px rgba(0,0,0,0.2); font-size:0.75rem; line-height:1.4; color:#121212; max-height:40%; overflow:hidden;">{html.escape(caption_text)}</div>' if caption_text else ''}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
    
    # Action buttons  
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Previous", disabled=current_idx == 0, type="secondary"):
            st.session_state.current_image_index = current_idx - 1
            st.rerun()
    
    with col2:
        # Only show accept if image is generated
        if current_idx < len(st.session_state.generated_images) and st.session_state.generated_images[current_idx].get("image_b64"):
            if st.button("Accept & Continue" if current_idx < len(screens) - 1 else " Accept & Finish", type="primary"):
                try:
                    # Save screens with edits
                    course_title = st.session_state.form_data["course"].get("course_title", "")
                    module_title = st.session_state.form_data["project"].get("module_title", "")
                    course_name = "".join(c for c in course_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
                    module_name = "".join(c for c in module_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
                    screens_filepath = f"data/{course_name}/{module_name}/text_outputs/screens.json"
                    os.makedirs(os.path.dirname(screens_filepath), exist_ok=True)
                    with open(screens_filepath, 'w') as f:
                        json.dump(st.session_state.screen_data, f, indent=2)
                    
                    # Save generated images
                    images_filepath = f"data/{course_name}/{module_name}/text_outputs/generated_images.json"
                    os.makedirs(os.path.dirname(images_filepath), exist_ok=True)
                    with open(images_filepath, 'w') as f:
                        json.dump(st.session_state.generated_images, f, indent=2)
                    
                    st.session_state.generated_images[current_idx]["accepted"] = True
                    if current_idx < len(screens) - 1:
                        st.session_state.current_image_index = current_idx + 1
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving: {str(e)}")
                finally:
                    _persist_generated_images()
    
    with col3:
        if current_idx < len(st.session_state.generated_images) and st.session_state.generated_images[current_idx].get("image_b64"):
            if st.button("Regenerate Image", type="secondary"):
                st.session_state.generated_images[current_idx]["image_b64"] = None
                st.session_state.regenerate_image = current_idx
                _persist_generated_images()
                st.rerun()


def step_final_preview():
    """Step 7: Review final images and captions in a slideshow."""
    st.markdown('<div class="step-header">Scene-by-Scene Preview</div>', unsafe_allow_html=True)
    
    screens = st.session_state.screen_data.get("screens", [])
    images = st.session_state.get("generated_images", [])
    if not isinstance(images, list):
        images = []
    ready = (
        screens
        and len(images) >= len(screens)
        and all(images[i].get("image_b64") for i in range(len(screens)))
    )

    # if not ready:
    #     st.warning("Complete image generation for every screen before opening the slideshow.")
    #     if st.button("Return to Image Generation", type="primary"):
    #         st.session_state.current_step = 6
    #         st.rerun()
    #     return

    if "preview_index" not in st.session_state or st.session_state.preview_index >= len(screens):
        st.session_state.preview_index = 0

    idx = st.session_state.preview_index
    caption = screens[idx].get("caption", "")
    image_b64 = ""
    if idx < len(images) and images[idx]:
        image_b64 = images[idx].get("image_b64", "")
    image_data_uri = f"data:image/png;base64,{image_b64}" if image_b64 else ""
    
    if st.session_state.get("should_save_composited", False):
        output_folder = _save_composited_images(screens, images)
        st.session_state.should_save_composited = False
        st.success(f"Composited screens saved to: {output_folder}")

    st.markdown(
        f"Captions and image descriptions remain available in `screens.json`. Right click and press 'Save Image As...' to save the image to your computer."
    )
    st.markdown(f"Screen {idx + 1} of {len(screens)}")

    st.markdown(
        f"""
        <div style="position:relative; display:block; width:100%; max-width:960px; margin:0 auto;">
            <img src="{image_data_uri}" style="width:100%; border-radius:18px;">
            <div style="
                position:absolute;
                left:24px;
                right:24px;
                bottom:24px;
                background:rgba(255,255,255,0.94);
                border-radius:14px;
                padding:18px 22px;
                box-shadow:0 8px 24px rgba(0,0,0,0.2);
                font-size:1rem;
                line-height:1.55;
                color:#121212;">
                {html.escape(caption)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # whitespace between image and buttons
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    def _go_prev():
        i = st.session_state.get("preview_index", 0)
        st.session_state.preview_index = max(i - 1, 0)

    def _go_next(total):
        i = st.session_state.get("preview_index", 0)
        st.session_state.preview_index = min(i + 1, total - 1)

    # place this block directly under the image, in the SAME parent column as the image
    # narrow center columns for arrows, large spacers on sides
    st.markdown("<div class='ace-nav'>", unsafe_allow_html=True)
    cols = st.columns([1, 0.2, 0.2, 1], gap="small")

    with cols[1]:
        st.button("◀", key="preview_prev",
                disabled=idx <= 0,
                use_container_width=True,
                on_click=_go_prev)

    with cols[2]:
        st.button("▶", key="preview_next",
                disabled=idx >= len(screens) - 1,
                use_container_width=True,
                on_click=_go_next, args=(len(screens),))

    with cols[3]:
        # st.markdown("<div class='ace-nav-back'>", unsafe_allow_html=True)
        st.button("Back to Image Generation",
                key="back_to_images",
                type="secondary",
                on_click=lambda: st.session_state.__setitem__("current_step", 6))
        # st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)