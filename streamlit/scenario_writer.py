"""
Scenario writer module for generating LLM-based scenario descriptions and content.
"""
import json
import os
import streamlit as st
from typing import Dict, List, Any


def generate_scenario_description(form_data: Dict[str, Any]) -> str:
    """
    Generate a scenario description based on the project brief.
    This is a placeholder for LLM integration.
    """
    course_data = form_data.get("course", {})
    project_data = form_data.get("project", {})
    audience_data = form_data.get("audience", {})
    
    # Extract key information
    course_title = course_data.get("course_title", "")
    project_title = project_data.get("project_title", "")
    project_goal = project_data.get("project_goal", "")
    project_objectives = project_data.get("project_learning_objectives", "")
    student_description = audience_data.get("student_description", "")
    education_level = audience_data.get("education_level", "")
    
    # Generate scenario description (placeholder - replace with actual LLM call)
    scenario_description = f"""
**Scenario: {project_title}**

**Context:**
Students in this {education_level.replace('_', ' ')} course are working on a project titled "{project_title}" as part of the "{course_title}" curriculum.

**Student Profile:**
{student_description}

**Project Goal:**
{project_goal}

**Learning Objectives:**
{project_objectives}

**Scenario Overview:**
This scenario presents students with a realistic challenge that requires them to apply their knowledge and skills to solve a practical problem. The scenario is designed to be engaging and relevant to their educational level and background.

**Expected Outcomes:**
Students will demonstrate their understanding by completing the project requirements while developing critical thinking, problem-solving, and practical application skills.
"""
    
    return scenario_description.strip()


def generate_image_vibe(style_pack: Dict[str, Any]) -> str:
    """
    Generate overall image vibe description based on style pack.
    """
    palette = style_pack.get("palette", "blue")
    vibe = style_pack.get("vibe", "flat_illustration")
    aspect_ratio = style_pack.get("aspect_ratio", "4:3")
    
    vibe_description = f"""
**Visual Style Guidelines:**

**Color Palette:** {palette}
**Visual Style:** {vibe.replace('_', ' ').title()}
**Aspect Ratio:** {aspect_ratio}

**Image Characteristics:**
- Consistent with the {vibe.replace('_', ' ')} aesthetic
- Colors should follow the {palette} palette
- Maintain {aspect_ratio} aspect ratio for all images
- Professional yet engaging visual presentation
- Clear, readable elements suitable for educational content
"""
    
    return vibe_description.strip()


def generate_initial_screens(form_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Generate initial list of screens with empty image descriptions and placeholder captions.
    """
    project_data = form_data.get("project", {})
    project_title = project_data.get("project_title", "Project")
    
    # Generate initial screens (placeholder - replace with actual LLM call)
    screens = [
        {
            "screen_number": 1,
            "title": f"Introduction to {project_title}",
            "image_description": "",  # To be filled later
            "caption_description": "Welcome screen introducing the project and its objectives"
        },
        {
            "screen_number": 2,
            "title": "Problem Statement",
            "image_description": "",  # To be filled later
            "caption_description": "Presenting the main challenge or problem to be solved"
        },
        {
            "screen_number": 3,
            "title": "Solution Approach",
            "image_description": "",  # To be filled later
            "caption_description": "Outlining the methodology and approach to solve the problem"
        },
        {
            "screen_number": 4,
            "title": "Implementation Steps",
            "image_description": "",  # To be filled later
            "caption_description": "Detailed steps for implementing the solution"
        },
        {
            "screen_number": 5,
            "title": "Results and Outcomes",
            "image_description": "",  # To be filled later
            "caption_description": "Expected results and learning outcomes from the project"
        }
    ]
    
    return screens


def generate_image_description_from_caption(caption: str, style_pack: Dict[str, Any]) -> str:
    """
    Generate image description (prompt style) from caption description.
    This should be replaced with actual LLM integration.
    """
    palette = style_pack.get("palette", "blue")
    vibe = style_pack.get("vibe", "flat_illustration")
    aspect_ratio = style_pack.get("aspect_ratio", "4:3")
    
    # Convert caption to image prompt (placeholder - replace with actual LLM call)
    image_prompt = f"""
Create an image for: {caption}

Style: {vibe.replace('_', ' ')}
Color palette: {palette}
Aspect ratio: {aspect_ratio}
Educational content style
Professional and engaging
Clear visual elements
Suitable for learning materials
"""
    
    return image_prompt.strip()


def save_scenario_data(scenario_data: Dict[str, Any], filepath: str) -> str:
    """
    Save scenario data to JSON file.
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Save to JSON
    with open(filepath, 'w') as f:
        json.dump(scenario_data, f, indent=2)
    
    return filepath


def load_scenario_data(filepath: str) -> Dict[str, Any]:
    """
    Load scenario data from JSON file.
    """
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {}


def get_scenario_filepath(form_data: Dict[str, Any]) -> str:
    """
    Get the filepath for scenario data based on course and module information.
    """
    course_title = form_data["course"].get("course_title", "unknown_course")
    module_title = form_data["project"].get("module_title", "unknown_module")
    
    # Clean names for directory structure
    course_name = "".join(c for c in course_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
    module_name = "".join(c for c in module_title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
    
    # Create filepath
    base_path = "data"
    course_path = os.path.join(base_path, course_name)
    module_path = os.path.join(course_path, module_name)
    text_outputs_path = os.path.join(module_path, "text_outputs")
    filename = "scenario_descriptions.json"
    
    return os.path.join(text_outputs_path, filename)
