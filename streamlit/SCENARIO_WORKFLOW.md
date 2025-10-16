# Scenario Generation Workflow

The AI Scenario Builder Tool now includes a comprehensive scenario generation workflow that extends beyond the initial project configuration.

## New Workflow Steps

### Step 7: Scenario Generation
- **Purpose**: Generate scenario description and image vibe based on project brief
- **Features**:
  - LLM-generated scenario description from course and project data
  - Image vibe generation based on style pack preferences
  - Option to regenerate or continue with existing data
  - Automatic saving of scenario data

### Step 8: Screen Management
- **Purpose**: Create and manage screens with caption descriptions
- **Features**:
  - Auto-generation of initial screens (5 default screens)
  - Editable caption descriptions for each screen
  - Add/remove screens functionality
  - Real-time validation of caption completeness
  - Screen status indicators

### Step 9: Image Description Generation
- **Purpose**: Generate image descriptions (prompts) from caption descriptions
- **Features**:
  - Automatic generation of image prompts from captions
  - Style pack integration for consistent visual guidelines
  - Editable image descriptions
  - Side-by-side comparison of captions and image descriptions

### Step 10: Final Review
- **Purpose**: Review complete scenario and export options
- **Features**:
  - Complete scenario overview
  - JSON export functionality
  - Formatted text export for manual copying
  - Option to start new project
  - Complete data visualization

## Data Structure

### Scenario Data Format
```json
{
  "scenario_description": "Generated scenario description...",
  "image_vibe": "Visual style guidelines...",
  "screens": [
    {
      "screen_number": 1,
      "title": "Screen Title",
      "image_description": "Generated image prompt...",
      "caption_description": "User-edited caption..."
    }
  ],
  "generated_at": "timestamp"
}
```

## File Organization

- **Configuration**: `module_generation_information.json` (original project data)
- **Scenario Data**: `scenario_data.json` (new scenario generation data)
- **Location**: `data/{course_name}/{module_name}/text_outputs/`

## Integration Points

### LLM Integration Ready
The scenario writer module includes placeholder functions for LLM integration:
- `generate_scenario_description()` - Replace with actual LLM call
- `generate_initial_screens()` - Replace with actual LLM call  
- `generate_image_description_from_caption()` - Replace with actual LLM call

### Style Pack Integration
All generated content respects the user's style preferences:
- Color palette
- Visual style (flat illustration, comic style, etc.)
- Aspect ratio
- Additional style information

## Usage Flow

1. Complete original workflow (Steps 1-6)
2. Click "Start Scenario Generation" in Step 6
3. Generate scenario description and image vibe (Step 7)
4. Create and edit screen captions (Step 8)
5. Generate image descriptions from captions (Step 9)
6. Review and export complete scenario (Step 10)

## Benefits

- **Automated Content Generation**: Reduces manual work for scenario creation
- **Consistent Styling**: All generated content follows user's style preferences
- **Flexible Editing**: Users can modify generated content at any step
- **Data Persistence**: All data is automatically saved and can be resumed
- **Export Options**: Multiple export formats for different use cases
