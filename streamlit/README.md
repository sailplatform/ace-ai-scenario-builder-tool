# AI Scenario Builder Tool

A user-friendly Streamlit application that guides educators through a structured workflow to collect course and project information for generating AI-assisted motivation slides and scenarios.

## Features

- **Streamlined workflow**: Simplified 4-step process for efficient project setup
- **Single-screen setup**: All essential information in one convenient form
- **Persistent optional fields**: Add detailed information at any time via sidebar
- **Course & Project Details**: Define course, module, and project information
- **Audience Profile**: Specify student background and description
- **Flexible configuration**: Required fields upfront, optional fields when needed
- **JSON Export**: Save complete configuration for further processing
- **Scenario Generation**: AI-powered scenario creation workflow

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run streamlit/app.py
```

## Usage

### Main Workflow
1. **Initial Selection**: Choose to create a new project or use existing content
2. **Project Setup**: Enter 5 essential fields:
   - Course Title
   - Module Title
   - Project Title
   - Project Goal
   - Brief Student Description
3. **Review & Save**: Review your information and save configuration
4. **Next Phase**: Proceed to scenario generation
5. **Scenario Generation**: Generate AI-powered scenarios for your project

### Optional Details (Available Anytime)
Access the sidebar panel at any step to add:
- Course Learning Objectives
- Module Description
- Project Learning Objectives
- Education Level
- Prerequisites
- Class Size

## Output Format

The tool generates a JSON file with the following structure:

```json
{
  "course": {
    "course_title": "Course name",
    "course_objectives": "List of course learning objectives."
  },
  "project": {
    "module_title": "Module name",
    "module_description": "Module description",
    "project_title": "Project name",
    "project_goal": "States overall outcome of project.",
    "project_learning_objectives": "List of project learning objectives"
  },
  "audience": {
    "student_description": "Who the students are",
    "education_level": "education_level",
    "prerequisites": ["string"],
    "class_size": "integer, optional"
  },
  "style_pack": {
    "palette": "color_palette",
    "vibe": "visual_style",
    "aspect_ratio": "4:3"
  }
}
```

## Next Steps

This JSON configuration can be used with AI tools to generate:
- Motivation slides with scenarios and captions
- Visual content based on the specified style preferences
- Contextualized activities for the defined audience
