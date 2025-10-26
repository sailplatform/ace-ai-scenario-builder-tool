"""
Utility functions for the AI Scenario Builder Tool.
"""
import json
import os
import streamlit as st


def save_to_json():
    """Save the collected data to a JSON file in the specified directory structure"""
    # Get course and module names for directory structure
    course_title = st.session_state.form_data["course"].get("course_title", "unknown_course")
    module_title = st.session_state.form_data["project"].get("module_title", "unknown_module")
    
    # Clean names for directory structure (remove spaces, special characters)
    course_name = "".join(c for c in course_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
    module_name = "".join(c for c in module_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
    
    # Create directory structure
    base_path = "data"
    course_path = os.path.join(base_path, course_name)
    module_path = os.path.join(course_path, module_name)
    text_outputs_path = os.path.join(module_path, "text_outputs")
    
    # Create directories if they don't exist
    os.makedirs(text_outputs_path, exist_ok=True)
    
    # Save JSON file
    filename = "context.json"
    filepath = os.path.join(text_outputs_path, filename)
    
    with open(filepath, 'w') as f:
        json.dump(st.session_state.form_data, f, indent=2)
    
    return filepath


def get_existing_courses():
    """Get list of existing courses from data directory"""
    courses = []
    data_path = "data"
    if os.path.exists(data_path):
        for item in os.listdir(data_path):
            item_path = os.path.join(data_path, item)
            if os.path.isdir(item_path):
                courses.append(item.replace('_', ' ').title())
    return sorted(courses)


def get_existing_modules(course_name):
    print(f"Getting existing modules for course: {course_name}")
    """Get list of existing modules for a given course"""
    modules = []
    course_name_clean = course_name.lower().replace(' ', '_')
    course_path = os.path.join("data", course_name_clean)
    
    if os.path.exists(course_path):
        for item in os.listdir(course_path):
            item_path = os.path.join(course_path, item)
            if os.path.isdir(item_path):
                modules.append(item.replace('_', ' ').title())
    return sorted(modules)
