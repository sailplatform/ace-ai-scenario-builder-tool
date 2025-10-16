"""
Step functions for the AI Scenario Builder Tool workflow.
"""
import json
import os
import streamlit as st
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
                        
                        # Skip directly to step 6 since both course and module exist
                        st.session_state.current_step = 6
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
            "Course Learning Objectives *",
            value=st.session_state.form_data["course"].get("course_objectives", ""),
            help="List the main learning objectives for this course (one per line or separated by commas)",
            height=100
        )
        
        submitted = st.form_submit_button("Continue to Project Information", type="primary")
        
        if submitted:
            if course_title and course_objectives:
                st.session_state.form_data["course"] = {
                    "course_title": course_title,
                    "course_objectives": course_objectives
                }
                st.session_state.current_step = 2
                st.rerun()
            else:
                st.error("Please fill in all required fields (marked with *)")


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
            "Module Description *",
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
            "Project Learning Objectives *",
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
                if all([module_title, module_description, project_title, project_goal, project_learning_objectives]):
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
                    st.error("Please fill in all required fields (marked with *)")


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
        
        st.subheader("Prerequisites")
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
            submitted = st.form_submit_button("Continue to Style →", type="primary")
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


def step_style_pack():
    """Step 4: Style Preferences"""
    st.markdown('<div class="step-header">🎨 Style Preferences</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-description">Define the visual style and additional information for your motivation slides.</div>', unsafe_allow_html=True)
    
    with st.form("style_pack_form"):
        st.subheader("Visual Style")
        
        # Style reference guide
        with st.expander("📚 Style Reference Guide", expanded=False):
            st.markdown("""
            **Common Color Palettes:**
            - `cool contrast` - blue and teal, navy and cyan
            - `warm contrast` - red and orange, coral and gold
            - `vibrant duo` - purple and yellow, magenta and lime
            - `earth duo` - brown and olive, tan and forest

            **Visual Style Examples:**
            - `comic panel style` - bold outlines, limited shading, expressive poses
            - `flat illustration design` - simple shapes, clean fills, minimal detail
            - `semi realistic rendering` - stylized proportions, moderate detail
            - `photo realistic imagery` - lifelike textures, accurate lighting
            - `minimalist visual language` - ample whitespace, few elements
            - `hand drawn sketch style` - pencil or ink lines, textured strokes
            - `three dimensional render` - modeled forms, perspective and lighting

            **Aspect Ratios:**
            - `4:3` - traditional presentation format
            - `16:9` - widescreen format
            - `1:1` - square format
            - `3:2` - photo format
            """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            palette = st.text_input(
                "Color Palette",
                value=st.session_state.form_data["style_pack"].get("palette", "blue"),
                help="Enter your preferred color palette (see reference guide above)"
            )
            
            vibe = st.text_input(
                "Visual Style",
                value=st.session_state.form_data["style_pack"].get("vibe", "flat_illustration"),
                help="Enter your preferred visual style (see reference guide above)"
            )
        
        with col2:
            aspect_ratio = st.text_input(
                "Aspect Ratio",
                value=st.session_state.form_data["style_pack"].get("aspect_ratio", "4:3"),
                help="Enter your preferred aspect ratio (see reference guide above)"
            )
        
        st.subheader("Additional Information")
        
        additional_info = st.text_area(
            "Additional Details",
            value=st.session_state.form_data.get("additional_info", ""),
            help="Specify any additional information such as characters, specific themes, cultural considerations, etc.",
            height=120
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("← Back to Audience", type="secondary")
            if submitted:
                st.session_state.current_step = 3
                st.rerun()
        
        with col2:
            submitted = st.form_submit_button("Review & Continue →", type="primary")
            if submitted:
                st.session_state.form_data["style_pack"] = {
                    "palette": palette,
                    "vibe": vibe,
                    "aspect_ratio": aspect_ratio
                }
                st.session_state.form_data["additional_info"] = additional_info
                st.session_state.current_step = 5
                st.rerun()


def step_review_export():
    """Step 5: Review and Save Configuration"""
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
    
    st.subheader("🎨 Style Preferences")
    style_data = st.session_state.form_data["style_pack"]
    st.markdown(f"**Color Palette:** {style_data.get('palette', 'blue')}")
    st.markdown(f"**Visual Style:** {style_data.get('vibe', 'flat_illustration').replace('_', ' ').title()}")
    st.markdown(f"**Aspect Ratio:** {style_data.get('aspect_ratio', '4:3')}")
    
    if st.session_state.form_data.get("additional_info"):
        st.subheader("📝 Additional Information")
        st.markdown(f"**Additional Details:** {st.session_state.form_data.get('additional_info', 'Not provided')}")
    
    # Save and continue options
    st.subheader("💾 Save Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Style", type="secondary"):
            st.session_state.current_step = 4
            st.rerun()
    
    with col2:
        if st.button("💾 Save & Continue", type="primary"):
            try:
                filepath = save_to_json()
                st.success(f"✅ Configuration saved successfully!")
                st.info(f"📁 Saved to: `{filepath}`")
                
                # Move to next step in workflow
                st.session_state.current_step = 6
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
    """Step 6: Next Phase - Scenario Generation"""
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
    
    st.subheader("⚙️ Workflow Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("✅ Configuration Complete")
        st.caption("Project details saved")
    
    with col2:
        st.info("⏳ Ready for Generation")
        st.caption("Next: Scenario creation")
    
    with col3:
        st.info("⏳ Pending")
        st.caption("Image generation")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Start New Project", type="secondary"):
            st.session_state.current_step = 0
            st.session_state.workflow_mode = None
            st.session_state.form_data = get_default_form_data()
            st.rerun()
    
    with col2:
        if st.button("📋 View Configuration", type="primary"):
            st.session_state.current_step = 5
            st.rerun()
    
    # Add new button to start scenario generation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Scenario Generation", type="primary", use_container_width=True):
            st.session_state.current_step = 7
            st.rerun()


def step_scenario_generation():
    """Step 7: Generate Scenario Description and Image Vibe"""
    st.markdown('<div class="step-header">📝 Scenario Generation</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-description">Generate scenario description and image vibe based on your project brief.</div>', unsafe_allow_html=True)
    
    # Check if scenario data already exists
    scenario_filepath = get_scenario_filepath(st.session_state.form_data)
    existing_scenario_data = load_scenario_data(scenario_filepath)
    
    if existing_scenario_data:
        st.info("📁 Existing scenario data found. You can regenerate or continue with existing data.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Regenerate Scenario", type="primary"):
                # Clear existing data and regenerate
                existing_scenario_data = {}
                st.rerun()
        
        with col2:
            if st.button("➡️ Continue with Existing", type="secondary"):
                st.session_state.scenario_data = existing_scenario_data
                st.session_state.current_step = 8
                st.rerun()
    
    # Generate new scenario data
    if not existing_scenario_data:
        with st.spinner("Generating scenario description and image vibe..."):
            # Generate scenario description
            scenario_description = generate_scenario_description(st.session_state.form_data)
            
            # Generate image vibe
            image_vibe = generate_image_vibe(st.session_state.form_data.get("style_pack", {}))
            
            # Store in session state
            st.session_state.scenario_data = {
                "scenario_description": scenario_description,
                "image_vibe": image_vibe,
                "screens": [],
                "generated_at": str(st.session_state.get("current_time", "unknown"))
            }
    
    # Display generated content
    st.subheader("📝 Generated Scenario Description")
    st.markdown(st.session_state.scenario_data.get("scenario_description", "No description generated"))
    
    st.subheader("🎨 Generated Image Vibe")
    st.markdown(st.session_state.scenario_data.get("image_vibe", "No vibe generated"))
    
    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Next Phase", type="secondary"):
            st.session_state.current_step = 6
            st.rerun()
    
    with col2:
        if st.button("💾 Save & Continue", type="primary"):
            try:
                # Save scenario data
                save_scenario_data(st.session_state.scenario_data, scenario_filepath)
                st.success("✅ Scenario data saved successfully!")
                st.session_state.current_step = 8
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error saving scenario data: {str(e)}")
    
    with col3:
        if st.button("🔄 Regenerate", type="secondary"):
            # Clear and regenerate
            st.session_state.scenario_data = {}
            st.rerun()


def step_screen_management():
    """Step 8: Manage Screens - Generate and Edit Caption Descriptions"""
    st.markdown('<div class="step-header">🖼️ Screen Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-description">Generate and manage screens with caption descriptions. Image descriptions will be generated from captions.</div>', unsafe_allow_html=True)
    
    # Initialize screens if not exists
    if "screens" not in st.session_state.scenario_data:
        st.session_state.scenario_data["screens"] = []
    
    screens = st.session_state.scenario_data["screens"]
    
    # Generate initial screens if empty
    if not screens:
        with st.spinner("Generating initial screens..."):
            screens = generate_initial_screens(st.session_state.form_data)
            st.session_state.scenario_data["screens"] = screens
            st.rerun()
    
    # Display screens
    st.subheader("📋 Generated Screens")
    
    for i, screen in enumerate(screens):
        with st.expander(f"Screen {screen['screen_number']}: {screen['title']}", expanded=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Caption description (editable)
                caption = st.text_area(
                    f"Caption Description for Screen {screen['screen_number']}",
                    value=screen.get("caption_description", ""),
                    height=100,
                    key=f"caption_{i}"
                )
                
                # Update the screen data
                screens[i]["caption_description"] = caption
            
            with col2:
                st.markdown("**Status:**")
                if caption.strip():
                    st.success("✅ Caption Ready")
                else:
                    st.warning("⚠️ Caption Empty")
                
                # Add/Remove screen buttons
                if st.button("🗑️ Remove", key=f"remove_{i}"):
                    screens.pop(i)
                    st.rerun()
    
    # Add new screen
    st.subheader("➕ Add New Screen")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        new_screen_title = st.text_input("Screen Title", key="new_screen_title")
    
    with col2:
        new_screen_caption = st.text_area("Caption Description", height=100, key="new_screen_caption")
    
    with col3:
        if st.button("➕ Add Screen", type="primary"):
            if new_screen_title and new_screen_caption:
                new_screen = {
                    "screen_number": len(screens) + 1,
                    "title": new_screen_title,
                    "image_description": "",
                    "caption_description": new_screen_caption
                }
                screens.append(new_screen)
                st.rerun()
            else:
                st.error("Please fill in both title and caption")
    
    # Navigation buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Scenario", type="secondary"):
            st.session_state.current_step = 7
            st.rerun()
    
    with col2:
        if st.button("💾 Save Screens", type="primary"):
            try:
                scenario_filepath = get_scenario_filepath(st.session_state.form_data)
                save_scenario_data(st.session_state.scenario_data, scenario_filepath)
                st.success("✅ Screens saved successfully!")
            except Exception as e:
                st.error(f"❌ Error saving screens: {str(e)}")
    
    with col3:
        if st.button("➡️ Generate Images", type="primary"):
            # Check if all screens have captions
            missing_captions = [s for s in screens if not s.get("caption_description", "").strip()]
            if missing_captions:
                st.error(f"❌ Please fill in captions for all screens. Missing: {len(missing_captions)} screens")
            else:
                st.session_state.current_step = 9
                st.rerun()


def step_image_generation():
    """Step 9: Generate Image Descriptions from Captions"""
    st.markdown('<div class="step-header">🎨 Image Description Generation</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-description">Generate image descriptions (prompts) from your caption descriptions.</div>', unsafe_allow_html=True)
    
    screens = st.session_state.scenario_data.get("screens", [])
    
    if not screens:
        st.error("No screens found. Please go back and create screens first.")
        if st.button("← Back to Screen Management"):
            st.session_state.current_step = 8
            st.rerun()
        return
    
    # Generate image descriptions
    with st.spinner("Generating image descriptions from captions..."):
        for i, screen in enumerate(screens):
            if not screen.get("image_description", "").strip():
                # Generate image description from caption
                caption = screen.get("caption_description", "")
                if caption:
                    image_desc = generate_image_description_from_caption(
                        caption, 
                        st.session_state.form_data.get("style_pack", {})
                    )
                    screens[i]["image_description"] = image_desc
    
    # Display results
    st.subheader("🎨 Generated Image Descriptions")
    
    for screen in screens:
        with st.expander(f"Screen {screen['screen_number']}: {screen['title']}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Caption Description:**")
                st.info(screen.get("caption_description", "No caption"))
            
            with col2:
                st.markdown("**Generated Image Description (Prompt):**")
                st.success(screen.get("image_description", "No image description"))
                
                # Allow manual editing
                edited_desc = st.text_area(
                    f"Edit Image Description for Screen {screen['screen_number']}",
                    value=screen.get("image_description", ""),
                    height=100,
                    key=f"edit_image_{screen['screen_number']}"
                )
                
                # Update if changed
                if edited_desc != screen.get("image_description", ""):
                    screen["image_description"] = edited_desc
    
    # Navigation buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Screens", type="secondary"):
            st.session_state.current_step = 8
            st.rerun()
    
    with col2:
        if st.button("💾 Save All", type="primary"):
            try:
                scenario_filepath = get_scenario_filepath(st.session_state.form_data)
                save_scenario_data(st.session_state.scenario_data, scenario_filepath)
                st.success("✅ All data saved successfully!")
            except Exception as e:
                st.error(f"❌ Error saving data: {str(e)}")
    
    with col3:
        if st.button("✅ Complete", type="primary"):
            st.session_state.current_step = 10
            st.rerun()


def step_final_review():
    """Step 10: Final Review and Export"""
    st.markdown('<div class="step-header">📋 Final Review</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-description">Review your complete scenario with all generated content.</div>', unsafe_allow_html=True)
    
    # Display complete scenario
    st.subheader("📝 Scenario Description")
    st.markdown(st.session_state.scenario_data.get("scenario_description", "No description"))
    
    st.subheader("🎨 Image Vibe")
    st.markdown(st.session_state.scenario_data.get("image_vibe", "No vibe"))
    
    st.subheader("🖼️ Screens Overview")
    screens = st.session_state.scenario_data.get("screens", [])
    
    for screen in screens:
        with st.expander(f"Screen {screen['screen_number']}: {screen['title']}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Caption:**")
                st.info(screen.get("caption_description", "No caption"))
            
            with col2:
                st.markdown("**Image Description:**")
                st.success(screen.get("image_description", "No image description"))
    
    # Export options
    st.subheader("📤 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export JSON", type="primary"):
            try:
                scenario_filepath = get_scenario_filepath(st.session_state.form_data)
                save_scenario_data(st.session_state.scenario_data, scenario_filepath)
                st.success(f"✅ Exported to: {scenario_filepath}")
            except Exception as e:
                st.error(f"❌ Export error: {str(e)}")
    
    with col2:
        if st.button("📋 Copy to Clipboard", type="secondary"):
            # Create a formatted text version
            formatted_text = f"""
SCENARIO: {st.session_state.form_data['project'].get('project_title', 'Unknown Project')}

DESCRIPTION:
{st.session_state.scenario_data.get('scenario_description', '')}

IMAGE VIBE:
{st.session_state.scenario_data.get('image_vibe', '')}

SCREENS:
"""
            for screen in screens:
                formatted_text += f"""
Screen {screen['screen_number']}: {screen['title']}
Caption: {screen.get('caption_description', '')}
Image Description: {screen.get('image_description', '')}
---
"""
            
            st.code(formatted_text)
            st.info("📋 Content formatted above - copy manually")
    
    with col3:
        if st.button("🔄 Start New Project", type="secondary"):
            # Reset everything
            st.session_state.current_step = 0
            st.session_state.workflow_mode = None
            st.session_state.form_data = get_default_form_data()
            st.session_state.scenario_data = {}
            st.rerun()
    
    # Navigation
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back to Images", type="secondary"):
            st.session_state.current_step = 9
            st.rerun()
    
    with col2:
        if st.button("📊 View Complete Data", type="primary"):
            st.json(st.session_state.scenario_data)
