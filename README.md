# Ace-AI Scenario Builder Tool

A Streamlit-based application that guides educators through a structured workflow to generate AI-assisted course scenarios and visuals from high-level project descriptions.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/sailplatform/ace-ai-scenario-builder-tool.git
cd ace-ai-scenario-builder-tool

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key (required for AI-powered features)
export OPENAI_API_KEY=your_openai_api_key_here

# Run the application
streamlit run streamlit/app.py
```

## Project Structure

### High-Level Architecture

The application follows a step-based workflow where users progress through sequential steps to build educational scenarios. Data is collected through forms, processed with AI assistance, and saved to a structured directory hierarchy under `data/`.

**Workflow Steps:**
1. **Initial Selection** (Step 0) - Choose new project or existing content
2. **Existing Content Selection** (Step 0.5) - Select course/module if using existing content
3. **Project Setup** (Step 1) - Enter course, module, and project details
4. **Review & Export** (Step 2) - Review and save configuration to JSON
5. **Scenario Generation** (Step 3) - Generate AI-powered scenario descriptions
6. **Scenario Metadata** (Step 4) - Define metadata, actors, and visual style
7. **Screen Generation** (Step 5) - Create screen captions and image descriptions
8. **Image Generation** (Step 6) - Generate images for each screen
9. **Final Preview** (Step 7) - Preview composited screens with captions

**Data Organization:**
```
data/
  {course_name}/
    {module_name}/
      text_outputs/
        context.json                    # Form data and project context
        scenario_descriptions.json      # Generated scenario text
        scenario_metadata.json          # Metadata, actors, visual style
        screens.json                    # Screen captions and image descriptions
        generated_images.json           # Base64-encoded generated images
        composited_screens/             # Final images with caption overlays
          screen_1.png
          screen_2.png
          ...
```

## File Descriptions

### `streamlit/app.py`
Main entry point for the Streamlit application. Handles page configuration, CSS injection, session state initialization, and routes to appropriate step functions based on `current_step` in session state.

**Key responsibilities:**
- Initialize session state via `config.initialize_session_state()`
- Apply custom CSS styling
- Display header and progress indicators
- Route to step functions based on workflow state

### `streamlit/config.py`
Manages session state and application configuration. Defines the data structure for form inputs and provides utilities for resetting state.

**Key functions:**
- `initialize_session_state()` - Sets up default session variables
- `get_default_form_data()` - Returns structured form data template
- `reset_session_state()` - Resets workflow to initial state
- `get_page_config()` - Returns Streamlit page configuration

### `streamlit/steps.py`
Contains all step function implementations for the workflow. Each step function handles UI rendering, form input collection, data validation, AI integration (OpenAI), and file persistence.

**Step functions:**
- `step_initial_selection()` - Workflow mode selection (new/existing)
- `step_existing_content_selection()` - Course and module selection from existing data
- `step_project_setup()` - Collect course, module, project, and audience information
- `step_review_export()` - Display summary and save `context.json`
- `step_scenario_generation()` - Generate scenario descriptions using OpenAI
- `step_scenario_metadata()` - Collect metadata, actors, and visual style preferences
- `step_screen_generation()` - Generate screen captions and image descriptions
- `step_image_generation()` - Generate images via OpenAI DALL-E API
- `step_final_preview()` - Display composited screens with captions and export options

**Helper functions:**
- `_get_text_output_dir()` - Constructs output directory path
- `_save_composited_images()` - Overlays captions on generated images
- `_persist_generated_images()` - Saves image data to JSON

### `streamlit/ui_components.py`
Handles UI styling, custom CSS, and reusable UI components.

**Key functions:**
- `get_custom_css()` - Returns CSS with brand colors and styling
- `display_progress()` - Renders step progress indicator
- `display_header()` - Displays application header
- `display_optional_details_modal()` - Sidebar panel for optional fields and editing (available from Step 2+)

**Features:**
- Brand color palette (Carnegie red, teal, gold, etc.)
- Custom button styling
- Progress indicator with step dots
- Sidebar with project information, optional fields, and editing capabilities

### `streamlit/utils.py`
Utility functions for file operations and data directory management.

**Key functions:**
- `save_to_json()` - Saves form data to `context.json` in structured directory
- `get_existing_courses()` - Scans `data/` directory for existing courses
- `get_existing_modules()` - Returns modules for a given course
- `save_scenario_data()` / `load_scenario_data()` - File I/O for scenario data
- `get_scenario_filepath()` - Constructs file paths for scenario data based on course/module names

### `requirements.txt`
Python dependencies:
- `streamlit>=1.28.0` - Web framework
- `openai>=1.0.0` - OpenAI API client for scenario and image generation
- `Pillow>=10.0.0` - Image processing for compositing captions

## Dependencies

- Python 3.7+
- OpenAI API key (set via environment variable)
- Required Python packages listed in `requirements.txt`
