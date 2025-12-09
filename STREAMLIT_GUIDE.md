# Streamlit Web Frontend - Quick Start Guide

## What Was Created

✅ **New File:** `src/streamlit_app.py` - A complete web-based GUI for the Content Strategy Generator

## Features

### 🎨 User Interface
- **8-Step Wizard:** Intuitive multi-step form for collecting brand information
- **Progress Tracking:** Visual progress indicator in sidebar
- **Responsive Design:** Clean, professional layout with custom CSS
- **Real-time Validation:** Input validation at each step

### 📋 Questionnaire Steps

1. **Brand Basics** - Name, industry, website
2. **Target Audience** - Detailed audience description
3. **Business Goals** - Select 1-4 primary goals
4. **Content Channels** - Choose active channels and primary channel
5. **Resources & Constraints** - Tone, budget, time, team resources
6. **Brand Details** - Unique value proposition, products/services
7. **Additional Context** - Competitors, past successes, strategy month
8. **Review & Generate** - Review all inputs and generate strategy

### 🚀 Capabilities

- Interactive form with validation
- Session state management
- Progress tracking
- Data review before generation
- Start over functionality
- Professional styling with custom CSS

## How to Run

### Option 1: Using the Virtual Environment (Recommended)

```bash
./venv/bin/streamlit run src/streamlit_app.py
```

### Option 2: If Streamlit is in PATH

```bash
streamlit run src/streamlit_app.py
```

### Option 3: With Port Specification

```bash
./venv/bin/streamlit run src/streamlit_app.py --server.port 8501
```

## Accessing the App

Once running, the app will be available at:
- **Local URL:** http://localhost:8501
- **Network URL:** Will be displayed in terminal

The browser should open automatically. If not, copy the Local URL into your browser.

## Features Overview

### Sidebar Navigation
- Progress indicator showing current step
- Visual step completion tracking
- "Start Over" button to reset the workflow

### Form Features
- **Required fields** marked with *
- **Help text** on hover for guidance
- **Examples** provided for complex fields
- **Back/Next** navigation buttons
- **Input persistence** - data saved as you navigate

### Data Collection

The app collects:
- Brand name and industry
- Target audience details
- Business goals (1-4 selections)
- Content channels (multiple with primary)
- Budget and time constraints
- Team resources
- Unique value proposition
- Products/services
- Competitors (optional)
- Past content successes (optional)
- Strategy month
- Additional notes (optional)

### Output Preview

At Step 8 (Review), you'll see:
- Complete summary of all inputs
- Option to go back and edit
- Generate button to start AI workflow

## Configuration

### Environment Variables Required

Make sure your `.env` file contains:
```
OPENROUTER_API_KEY=your_api_key_here
```

### Dependencies

All required packages are installed:
- streamlit >= 1.52.0
- streamlit-option-menu >= 0.4.0
- crewai, python-dotenv, etc.

## Stopping the App

To stop the Streamlit server:
- Press `Ctrl+C` in the terminal

## Tips

1. **Development Mode:** Streamlit auto-reloads when you save changes to the file
2. **Clear Cache:** Use `Ctrl+Shift+R` in browser to clear Streamlit cache
3. **Session State:** Data persists as you navigate through steps
4. **Mobile Friendly:** The app is responsive and works on mobile devices

## Customization

### To Modify Styling

Edit the CSS in the `st.markdown()` section (lines 40-65):
```python
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4A90E2;
        ...
    }
</style>
""", unsafe_allow_html=True)
```

### To Add More Steps

1. Add step name to `progress_steps` list
2. Create new `elif st.session_state.step == X:` block
3. Add form fields
4. Add Back/Next navigation

### To Modify Form Fields

Edit the respective step block and update:
- Field labels
- Options (for select boxes)
- Help text
- Validation rules

## Troubleshooting

### Port Already in Use
```bash
./venv/bin/streamlit run src/streamlit_app.py --server.port 8502
```

### Module Not Found
Make sure virtual environment is activated or use:
```bash
./venv/bin/streamlit run src/streamlit_app.py
```

### API Key Not Found
Check your `.env` file contains `OPENROUTER_API_KEY`

## Next Steps

To enable the full AI workflow in the Streamlit app:
1. The workflow execution code is prepared
2. Current version shows the interface and data collection
3. AI generation can be triggered from Step 8

## File Structure

```
content-strategy-crew/
├── src/
│   ├── streamlit_app.py        ← NEW! Web frontend
│   ├── cli_workflow.py          
│   ├── interactive_workflow.py  
│   ├── main.py                  
│   └── ...
├── .env                         ← Make sure this exists
├── requirements.txt             ← Updated with Streamlit
└── STREAMLIT_GUIDE.md          ← This file
```

---

**Created:** December 8, 2025
**Streamlit Version:** 1.52.1
**Status:** ✅ Ready to use
