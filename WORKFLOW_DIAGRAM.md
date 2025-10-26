# AI Scenario Builder - Workflow Diagram

## Old Workflow (Before Changes)
```
Step 0: Initial Selection
    ↓
Step 0.5: Existing Content Selection (if "Use Existing" chosen)
    ↓
Step 1: Course Information
    - Course Title *
    - Course Learning Objectives (Optional)
    ↓
Step 2: Project Information
    - Module Title *
    - Module Description (Optional)
    - Project Title *
    - Project Goal *
    - Project Learning Objectives (Optional)
    ↓
Step 3: Audience Information
    - Student Description *
    - Education Level *
    - Prerequisites (Optional)
    - Class Size (Optional)
    ↓
Step 4: Review & Save
    ↓
Step 5: Next Phase
    ↓
Step 6: Scenario Generation
```

## New Workflow (After Changes)
```
Step 0: Initial Selection
    ↓
Step 0.5: Existing Content Selection (if "Use Existing" chosen)
    ↓
Step 1: Project Setup (COMBINED)
    REQUIRED FIELDS:
    - Course Title *
    - Module Title *
    - Project Title *
    - Project Goal *
    - Brief Student Description *
    ↓
Step 2: Review & Save
    ↓
Step 3: Next Phase
    ↓
Step 4: Scenario Generation

┌─────────────────────────────────────────────────────┐
│  SIDEBAR (Persistent across all steps 1-4)        │
│  ┌───────────────────────────────────────────┐     │
│  │  📝 Optional Information                  │     │
│  │  📋 Edit Optional Details (Expander)      │     │
│  │     ├── Course Learning Objectives        │     │
│  │     ├── Module Description                │     │
│  │     ├── Project Learning Objectives       │     │
│  │     ├── Education Level                   │     │
│  │     ├── Prerequisites                     │     │
│  │     └── Class Size                        │     │
│  │  [💾 Save Optional Details]               │     │
│  └───────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────┘
```

## Key Improvements

### 1. Reduced Form Complexity
- **Before:** 3 separate forms with mix of required/optional fields
- **After:** 1 simple form with only 5 required fields

### 2. Optional Fields Access
- **Before:** Mixed into the main workflow steps
- **After:** Available in sidebar at any time during steps 1-4

### 3. Step Reduction
- **Before:** 6 main workflow steps
- **After:** 4 main workflow steps (33% reduction)

### 4. User Flexibility
- **Before:** Must fill optional fields at specific steps
- **After:** Can add optional details whenever convenient

### 5. Time to First Milestone
- **Before:** 3 forms → ~5-10 minutes to reach Review & Save
- **After:** 1 form → ~2-3 minutes to reach Review & Save

## Data Flow

```
User Input (Step 1: Project Setup)
    ↓
session_state.form_data = {
    "course": {
        "course_title": "[user input]",
        "course_objectives": "[from sidebar or empty]"
    },
    "project": {
        "module_title": "[user input]",
        "module_description": "[from sidebar or empty]",
        "project_title": "[user input]",
        "project_goal": "[user input]",
        "project_learning_objectives": "[from sidebar or empty]"
    },
    "audience": {
        "student_description": "[user input]",
        "education_level": "[from sidebar or default]",
        "prerequisites": "[from sidebar or empty]",
        "class_size": "[from sidebar or default 25]"
    }
}
    ↓
Step 2: Review & Save
    ↓
JSON Export (same format as before)
```

## Backward Compatibility

✅ **Existing JSON files:** Will work perfectly with new interface
✅ **Data structure:** Unchanged - maintains same format
✅ **Optional fields:** Have sensible defaults if not provided
✅ **Existing content selection:** Still works as before

