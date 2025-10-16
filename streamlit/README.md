# AI Scenario Builder Tool

A user-friendly Streamlit application that guides educators through a structured workflow to collect course and project information for generating AI-assisted motivation slides and scenarios.

## Features

- **Step-by-step workflow**: Intuitive 6-step process that gradually collects information
- **Course Information**: Collect course title and learning objectives
- **Project Details**: Define module and project information with goals and objectives
- **Motivation & Problem**: Define problem statements and success criteria
- **Audience Profile**: Specify student background, education level, and prerequisites
- **Style Preferences**: Choose visual style, color palette, and aspect ratio
- **JSON Export**: Download complete configuration for further processing

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

1. **Course Information**: Enter your course title and learning objectives
2. **Project Information**: Define the module and project details
3. **Motivation**: Describe the problem and success criteria
4. **Audience**: Specify student background and prerequisites
5. **Style**: Choose visual preferences for slides
6. **Review & Export**: Review all information and download JSON configuration

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
