# -*- coding: utf-8 -*-
import streamlit as st
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process

# Add src directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables
load_dotenv()

# ================================
# SECURITY IMPORTS
# ================================
from security import InputValidator, RateLimiter, BetaAuthenticator
from config import config, check_configuration
from utils.secure_logger import logger, log_user_action, log_generation_start, log_generation_complete, log_error

# ================================
# CONFIGURE API WITH SECURITY
# ================================
api_key = config.get_api_key()
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
    os.environ["OPENAI_MODEL_NAME"] = "anthropic/claude-sonnet-4-20250514"

from main import (
    brand_analyst,
    strategy_architect,
    content_calendar_specialist
)
from document_generator import generate_strategy_docx, generate_calendar_docx
from excel_generator import generate_content_calendar_xlsx
from content_parser import ContentCalendarParser, parse_strategies_output
import json
import yaml

# Page configuration
st.set_page_config(
    page_title="AI Content Marketing Strategist",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4A90E2;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2C3E50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #4A90E2;
        padding-bottom: 0.5rem;
    }
    .stProgress > div > div > div > div {
        background-color: #4A90E2;
    }
    .success-box {
        padding: 1rem;
        background-color: #D4EDDA;
        border-left: 5px solid #28A745;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ================================
# SECURITY: Configuration Check
# ================================
check_configuration()

# ================================
# SECURITY: Authentication
# ================================
# Initialize authenticator based on environment
if config.is_production():
    beta_password = config.get_beta_password()
    authenticator = BetaAuthenticator(password=beta_password)
else:
    from security.auth import DevelopmentAuthenticator
    authenticator = DevelopmentAuthenticator()

# Show login form if not authenticated
if not authenticator.show_login_form():
    st.stop()

# ================================
# SECURITY: Initialize Security Modules
# ================================
# Initialize input validator
validator = InputValidator()

# Initialize rate limiter based on environment
if config.is_production():
    rate_limit_config = config.get_rate_limit_config()
    rate_limiter = RateLimiter(
        max_requests=rate_limit_config['max_requests'],
        window_seconds=rate_limit_config['window_seconds']
    )
else:
    from security.rate_limiter import DevelopmentRateLimiter
    rate_limiter = DevelopmentRateLimiter()

# Log application start
logger.info("Application loaded successfully", context={'environment': config.environment.value})

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'brand_data' not in st.session_state:
    st.session_state.brand_data = {}
if 'workflow_complete' not in st.session_state:
    st.session_state.workflow_complete = False
if 'strategies_generated' not in st.session_state:
    st.session_state.strategies_generated = False
if 'calendar_generated' not in st.session_state:
    st.session_state.calendar_generated = False
if 'strategies_output' not in st.session_state:
    st.session_state.strategies_output = None
if 'calendar_output' not in st.session_state:
    st.session_state.calendar_output = None
if 'brand_analysis_output' not in st.session_state:
    st.session_state.brand_analysis_output = None

def reset_workflow():
    """Reset the workflow to start over"""
    st.session_state.step = 1
    st.session_state.brand_data = {}
    st.session_state.workflow_complete = False
    st.session_state.strategies_generated = False
    st.session_state.calendar_generated = False
    st.session_state.strategies_output = None
    st.session_state.calendar_output = None
    st.session_state.brand_analysis_output = None

    # Clear ALL session state keys to prevent caching issues
    keys_to_delete = [
        'generating',
        'selected_strategy',
        'calendar_generation',
        'generating_calendar',
        'analyze_brand_task',
        'generate_strategies_task',
        'phase1_crew',
        'phase2_crew'
    ]

    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]

    # Delete output files to prevent showing old content
    output_files = [
        "outputs/1_brand_analysis.md",
        "outputs/2_five_strategies.md",
        "outputs/3_content_calendar.md",
        "outputs/strategy_options.docx",
        "outputs/content_calendar.docx",
        "outputs/content_calendar.xlsx",
        "outputs/streamlit_output.json",
        "outputs/streamlit_output.yaml"
    ]

    for file in output_files:
        try:
            if os.path.exists(file):
                os.remove(file)
        except:
            pass

# Sidebar navigation
with st.sidebar:
    st.markdown("### 🎯 AI Content Marketing Strategist")
    st.markdown("---")

    # Controls section
    st.markdown("### 🎛️ Controls")

    if st.button("🗑️ Clear Cache & Start Fresh", help="Reset all data and start over", use_container_width=True):
        reset_workflow()
        st.rerun()

    # Logout button (if authenticated)
    authenticator.show_logout_button()

    # Show remaining requests
    if config.is_production():
        remaining = rate_limiter.get_remaining_requests()
        if remaining > 0:
            st.info(f"📊 **{remaining}** generations remaining")

    st.markdown("---")

    # Status indicators
    if st.session_state.strategies_generated:
        st.success("✅ Strategies Generated")

    if st.session_state.calendar_generated:
        st.success("✅ Calendar Generated")

    if st.session_state.workflow_complete:
        st.success("🎉 Workflow Complete!")

    if st.session_state.strategies_generated or st.session_state.calendar_generated:
        st.markdown("---")

    # Progress indicator
    progress_steps = [
        "📋 Brand Basics",
        "👥 Target Audience",
        "🎯 Business Goals",
        "📱 Content Channels",
        "⚙️ Resources",
        "💡 Brand Details",
        "📝 Additional Info",
        "✅ Review & Generate"
    ]

    current_step = st.session_state.step
    st.markdown("#### Progress")
    progress = (current_step - 1) / len(progress_steps)
    st.progress(progress)
    st.markdown(f"**Step {current_step} of {len(progress_steps)}**")

    st.markdown("---")

    # Current step highlight
    for i, step_name in enumerate(progress_steps, 1):
        if i < current_step:
            st.markdown(f"✅ {step_name}")
        elif i == current_step:
            st.markdown(f"**🔵 {step_name}**")
        else:
            st.markdown(f"⚪ {step_name}")

    st.markdown("---")

    if st.button("🔄 Start Over"):
        reset_workflow()
        st.rerun()

    # Log viewer (development mode only)
    if not config.is_production():
        st.markdown("---")
        logger.show_log_viewer()

# Main content
st.markdown('<div class="main-header">🎯 AI Content Marketing Strategist</div>', unsafe_allow_html=True)

# Step 1: Brand Basics
if st.session_state.step == 1:
    st.markdown('<div class="section-header">📋 Step 1: Brand Basics</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        brand_name = st.text_input(
            "Brand Name *",
            value=st.session_state.brand_data.get('brand_name', ''),
            help="Enter your brand or company name"
        )

    with col2:
        industry = st.selectbox(
            "Industry *",
            options=[
                "B2B SaaS", "E-commerce - Fashion", "E-commerce - Electronics",
                "Local Services", "Healthcare", "Education", "Finance",
                "Real Estate", "Food & Beverage", "Travel & Hospitality",
                "Marketing Agency", "Consulting", "Manufacturing",
                "Non-Profit", "Entertainment", "Technology Hardware",
                "Professional Services", "Home Services", "Automotive",
                "Beauty & Wellness", "Sports & Fitness", "Media & Publishing",
                "Other"
            ],
            index=0 if 'industry' not in st.session_state.brand_data else
                  ["B2B SaaS", "E-commerce - Fashion", "E-commerce - Electronics",
                "Local Services", "Healthcare", "Education", "Finance",
                "Real Estate", "Food & Beverage", "Travel & Hospitality",
                "Marketing Agency", "Consulting", "Manufacturing",
                "Non-Profit", "Entertainment", "Technology Hardware",
                "Professional Services", "Home Services", "Automotive",
                "Beauty & Wellness", "Sports & Fitness", "Media & Publishing",
                "Other"].index(st.session_state.brand_data['industry'])
        )

    website = st.text_input(
        "Company Website (Optional)",
        value=st.session_state.brand_data.get('website', ''),
        help="Your company website URL"
    )

    if st.button("Next →", key="next_1"):
        if brand_name:
            st.session_state.brand_data['brand_name'] = brand_name
            st.session_state.brand_data['industry'] = industry
            st.session_state.brand_data['website'] = website
            st.session_state.step = 2
            st.rerun()
        else:
            st.error("Please enter a brand name")

# Step 2: Target Audience
elif st.session_state.step == 2:
    st.markdown('<div class="section-header">👥 Step 2: Target Audience</div>', unsafe_allow_html=True)

    target_audience = st.text_area(
        "Describe your target audience in detail *",
        value=st.session_state.brand_data.get('target_audience', ''),
        height=200,
        help="Who are they? What are their pain points? What motivates them?"
    )

    st.markdown("**Example:**")
    st.info("Marketing teams at mid-size companies (50-500 employees) who need better project management tools. They're frustrated with disjointed workflows and spending too much time in meetings.")

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("Next →", key="next_2"):
            if len(target_audience) >= 50:
                st.session_state.brand_data['target_audience'] = target_audience
                st.session_state.step = 3
                st.rerun()
            else:
                st.error("Please provide a more detailed description (at least 50 characters)")

# Step 3: Business Goals
elif st.session_state.step == 3:
    st.markdown('<div class="section-header">🎯 Step 3: Business Goals</div>', unsafe_allow_html=True)

    st.markdown("Select your primary business goals (choose 1-4):")

    goals_options = [
        "Brand Awareness",
        "Lead Generation",
        "Sales",
        "Product Education",
        "Community Building",
        "Customer Retention",
        "Thought Leadership"
    ]

    selected_goals = []
    cols = st.columns(2)
    for i, goal in enumerate(goals_options):
        with cols[i % 2]:
            if st.checkbox(
                goal,
                value=goal in st.session_state.brand_data.get('business_goals', []),
                key=f"goal_{i}"
            ):
                selected_goals.append(goal)

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("Next →", key="next_3"):
            if 1 <= len(selected_goals) <= 4:
                st.session_state.brand_data['business_goals'] = selected_goals
                st.session_state.step = 4
                st.rerun()
            else:
                st.error("Please select 1-4 business goals")

# Step 4: Content Channels
elif st.session_state.step == 4:
    st.markdown('<div class="section-header">📱 Step 4: Content Channels</div>', unsafe_allow_html=True)

    st.markdown("**Which channels do you want to focus on?**")

    channels_options = [
        "LinkedIn", "Twitter", "Instagram", "Facebook",
        "TikTok", "Blog", "YouTube", "Pinterest",
        "Email Newsletter", "Podcast", "Medium"
    ]

    selected_channels = []
    cols = st.columns(3)
    for i, channel in enumerate(channels_options):
        with cols[i % 3]:
            if st.checkbox(
                channel,
                value=channel in st.session_state.brand_data.get('active_channels', []),
                key=f"channel_{i}"
            ):
                selected_channels.append(channel)

    # NEW: Multiple primary channels
    primary_channels = []
    if selected_channels:
        st.markdown("---")
        st.markdown("**Select 1-3 PRIMARY channels** (where you'll focus most effort):")
        st.caption("Primary channels will get 60-70% of your content. Other selected channels will get the remaining 30-40%.")

        primary_cols = st.columns(min(len(selected_channels), 4))
        for i, channel in enumerate(selected_channels):
            with primary_cols[i % 4]:
                if st.checkbox(
                    f"✨ {channel}",
                    value=channel in st.session_state.brand_data.get('primary_channels', []),
                    key=f"primary_{i}",
                    help="Mark as primary focus"
                ):
                    primary_channels.append(channel)

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("Next →", key="next_4"):
            if selected_channels and 1 <= len(primary_channels) <= 3:
                st.session_state.brand_data['active_channels'] = selected_channels
                st.session_state.brand_data['primary_channels'] = primary_channels
                st.session_state.brand_data['secondary_channels'] = [c for c in selected_channels if c not in primary_channels]
                st.session_state.step = 5
                st.rerun()
            elif not selected_channels:
                st.error("Please select at least one channel")
            elif len(primary_channels) == 0:
                st.error("Please select at least 1 primary channel")
            elif len(primary_channels) > 3:
                st.error("Please select no more than 3 primary channels")

# Step 5: Resources & Constraints
elif st.session_state.step == 5:
    st.markdown('<div class="section-header">⚙️ Step 5: Resources & Constraints</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        brand_tone = st.selectbox(
            "Brand Tone *",
            options=[
                "Professional & Corporate",
                "Professional yet Approachable",
                "Casual & Friendly",
                "Playful & Fun",
                "Authoritative & Expert",
                "Inspirational & Aspirational"
            ]
        )

        monthly_budget = st.selectbox(
            "Monthly Content Budget *",
            options=[
                "Under $500",
                "$500 - $1,000",
                "$1,000 - $2,500",
                "$2,500 - $5,000",
                "$5,000 - $10,000",
                "$10,000+"
            ]
        )

    with col2:
        time_commitment = st.selectbox(
            "Weekly Time Commitment *",
            options=[
                "5-10 hours/week",
                "10-20 hours/week",
                "20-30 hours/week",
                "30+ hours/week"
            ]
        )

    st.markdown("**What content creation resources do you have?**")

    resources_options = [
        "In-house writer",
        "In-house designer",
        "In-house video editor",
        "Freelancers",
        "AI tools (ChatGPT, etc.)",
        "No dedicated resources"
    ]

    selected_resources = []
    cols = st.columns(3)
    for i, resource in enumerate(resources_options):
        with cols[i % 3]:
            if st.checkbox(
                resource,
                value=resource in st.session_state.brand_data.get('resources', []),
                key=f"resource_{i}"
            ):
                selected_resources.append(resource)

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.step = 4
            st.rerun()
    with col2:
        if st.button("Next →", key="next_5"):
            if selected_resources:
                st.session_state.brand_data['brand_tone'] = brand_tone
                st.session_state.brand_data['monthly_budget'] = monthly_budget
                st.session_state.brand_data['time_commitment'] = time_commitment
                st.session_state.brand_data['resources'] = selected_resources
                st.session_state.step = 6
                st.rerun()
            else:
                st.error("Please select at least one resource")

# Step 6: Brand Details
elif st.session_state.step == 6:
    st.markdown('<div class="section-header">💡 Step 6: Brand Details</div>', unsafe_allow_html=True)

    unique_value_prop = st.text_area(
        "Unique Value Proposition *",
        value=st.session_state.brand_data.get('unique_value_prop', ''),
        height=150,
        help="What makes you different from competitors?"
    )

    products_services = st.text_input(
        "Key Products/Services (comma-separated) *",
        value=st.session_state.brand_data.get('products_services', ''),
        help="e.g., Project management platform, Team collaboration suite"
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.step = 5
            st.rerun()
    with col2:
        if st.button("Next →", key="next_6"):
            if unique_value_prop and products_services:
                st.session_state.brand_data['unique_value_prop'] = unique_value_prop
                st.session_state.brand_data['products_services'] = products_services
                st.session_state.step = 7
                st.rerun()
            else:
                st.error("Please fill in all required fields")

# Step 7: Additional Context
elif st.session_state.step == 7:
    st.markdown('<div class="section-header">📝 Step 7: Additional Context</div>', unsafe_allow_html=True)

    competitors = st.text_input(
        "Main Competitors (comma-separated, optional)",
        value=st.session_state.brand_data.get('competitors', ''),
        help="e.g., Asana, Monday.com, ClickUp"
    )

    past_successes = st.text_area(
        "Past Content That Worked Well (optional)",
        value=st.session_state.brand_data.get('past_successes', ''),
        height=100,
        help="Any content types or topics that performed well in the past"
    )

    strategy_month = st.selectbox(
        "Which month should we plan for? *",
        options=[
            "January 2025", "February 2025", "March 2025",
            "April 2025", "May 2025", "June 2025",
            "July 2025", "August 2025", "September 2025"
        ]
    )

    additional_notes = st.text_area(
        "Additional Notes (optional)",
        value=st.session_state.brand_data.get('additional_notes', ''),
        height=100,
        help="Any other context or specific requirements"
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.step = 6
            st.rerun()
    with col2:
        if st.button("Next → Review", key="next_7"):
            st.session_state.brand_data['competitors'] = competitors
            st.session_state.brand_data['past_successes'] = past_successes
            st.session_state.brand_data['strategy_month'] = strategy_month
            st.session_state.brand_data['additional_notes'] = additional_notes
            st.session_state.step = 8
            st.rerun()

# Step 8: Review & Generate
elif st.session_state.step == 8:
    st.markdown('<div class="section-header">✅ Step 8: Review & Generate</div>', unsafe_allow_html=True)

    st.markdown("### Review Your Information")

    # Display summary
    data = st.session_state.brand_data

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Brand Information**")
        st.write(f"**Brand:** {data.get('brand_name', 'N/A')}")
        st.write(f"**Industry:** {data.get('industry', 'N/A')}")
        st.write(f"**Website:** {data.get('website', 'Not provided')}")

        st.markdown("**Business Goals**")
        for goal in data.get('business_goals', []):
            st.write(f"• {goal}")

        st.markdown("**Content Channels**")
        st.write(f"**Primary ({len(data.get('primary_channels', []))}):** {', '.join(data.get('primary_channels', []))}")
        if data.get('secondary_channels'):
            st.write(f"**Secondary:** {', '.join(data.get('secondary_channels', []))}")

    with col2:
        st.markdown("**Resources**")
        st.write(f"**Tone:** {data.get('brand_tone', 'N/A')}")
        st.write(f"**Budget:** {data.get('monthly_budget', 'N/A')}")
        st.write(f"**Time:** {data.get('time_commitment', 'N/A')}")

        st.markdown("**Team Resources**")
        for resource in data.get('resources', []):
            st.write(f"• {resource}")

        st.markdown("**Strategy Details**")
        st.write(f"**Month:** {data.get('strategy_month', 'N/A')}")

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("← Back to Edit"):
            st.session_state.step = 7
            st.rerun()

    with col2:
        if not st.session_state.get('generating', False):
            if st.button("🚀 Generate Strategy", type="primary", use_container_width=True):
                # ================================
                # SECURITY: Input Validation
                # ================================
                log_user_action("Initiated strategy generation", {'brand': data.get('brand_name')})

                # Validate all inputs
                is_valid, errors = validator.validate_all(data)

                if not is_valid:
                    st.error("❌ Please fix the following issues:")
                    for error in errors:
                        st.error(f"• {error}")
                    log_error(Exception(f"Validation failed: {errors}"), context={'brand': data.get('brand_name')})
                    st.stop()

                # ================================
                # SECURITY: Rate Limiting
                # ================================
                if not rate_limiter.is_allowed():
                    rate_limiter.show_rate_limit_message()
                    logger.warning("Rate limit exceeded", context={'brand': data.get('brand_name')})
                    st.stop()

                # Show remaining requests
                remaining = rate_limiter.get_remaining_requests()
                if remaining <= 2:
                    st.info(f"ℹ️ You have **{remaining}** generation{'s' if remaining != 1 else ''} remaining this hour")

                # All checks passed - proceed
                logger.info("Starting strategy generation", context={'brand': data.get('brand_name')})
                st.session_state.generating = True
                st.rerun()

# Run workflow if generating
if st.session_state.step == 8 and st.session_state.get('generating', False):
    st.markdown("---")
    st.markdown("## 🤖 AI Strategy Generation in Progress")

    data = st.session_state.brand_data

    # Format brand data for AI
    brand_data_text = f"""
Brand Name: {data['brand_name']}
Industry: {data['industry']}
Company Website: {data.get('website', 'Not provided')}
Target Audience: {data['target_audience']}
Business Goals: {', '.join(data['business_goals'])}
Active Channels: {', '.join(data['active_channels'])}
Primary Channels (60-70% of content): {', '.join(data.get('primary_channels', [data.get('primary_channel', '')]))}
Secondary Channels (30-40% of content): {', '.join(data.get('secondary_channels', []))}
Brand Tone: {data['brand_tone']}
Monthly Budget: {data['monthly_budget']}
Weekly Time Commitment: {data['time_commitment']}
Content Creation Resources: {', '.join(data['resources'])}
Unique Value Proposition: {data['unique_value_prop']}
Key Products/Services: {data['products_services']}
Competitors: {data.get('competitors', 'Not provided')}
Past Successful Content: {data.get('past_successes', 'Not provided')}
Strategy Month: {data['strategy_month']}
Additional Notes: {data.get('additional_notes', 'None')}

IMPORTANT: Distribute content across ALL active channels with primary channels receiving 60-70% of content and secondary channels receiving 30-40%. Ensure variety in channel distribution.
"""

    # Phase 1: Brand Analysis + Strategy Generation
    # ONLY RUN IF NOT ALREADY GENERATED
    if not st.session_state.strategies_generated:
        with st.status("📋 Phase 1: Analyzing brand and generating 5 strategy options...", expanded=True) as status1:
            st.write("🔄 Creating AI agents...")
            st.write("🔄 Running brand analysis...")

            try:
                analyze_brand = Task(
                    description=f"""
                    Analyze the following brand information and create a comprehensive brand profile:

                    {brand_data_text}

                    Your analysis should include:
                    1. Brand Positioning Summary (2-3 sentences)
                    2. Primary Audience Characteristics
                    3. Key Differentiators
                    4. Content Opportunities
                    5. Channel-Specific Considerations
                    6. Constraints & Resources
                    7. Strategic Imperatives

                    Be specific and insightful.
                    """,
                    expected_output="Comprehensive brand analysis",
                    agent=brand_analyst
                )

                # Get channel information
                primary_channels_str = ', '.join(data.get('primary_channels', []))
                secondary_channels_str = ', '.join(data.get('secondary_channels', []))
                all_channels_str = ', '.join(data.get('active_channels', []))

                generate_strategies = Task(
                    description=f"""
                    IMPORTANT: You must generate ALL 5 strategies in a single response.

                    Based on the brand analysis, create 5 COMPLETE AND DISTINCT content strategy options.

                    ⚠️ CRITICAL CHANNEL REQUIREMENTS - YOU MUST FOLLOW THESE EXACTLY:

                    THE BRAND HAS SELECTED THESE CHANNELS ONLY:
                    - Primary Channels (must appear in ALL strategies): {primary_channels_str}
                    - Secondary Channels: {secondary_channels_str}
                    - ALL Active Channels: {all_channels_str}

                    🚫 DO NOT USE: Any channels NOT in this list: {all_channels_str}
                    ✅ YOU MUST ONLY USE: {all_channels_str}
                    ⚠️ DO NOT mention LinkedIn, Twitter, Blog, TikTok, Instagram, Facebook, YouTube, or ANY channel unless it appears in: {all_channels_str}

                    For EACH of the 5 strategies, provide:

                    **Strategy [NUMBER]: [Name]**
                    **Tagline:** One memorable sentence
                    **Core Approach:** 2-3 sentences
                    **Content Pillars:** Pillar 1 | Pillar 2 | Pillar 3
                    **Posting Frequency:** ONLY use channels from [{all_channels_str}]. Example: "{primary_channels_str.split(',')[0].strip()} X/week" (adjust based on selected channels)
                    **Content Mix:** Educational [X]%, Promotional [X]%, Engagement [X]%
                    **Top 3 Content Ideas:** (must be relevant to channels: {all_channels_str})
                      1. [Title]
                      2. [Title]
                      3. [Title]
                    **Effort:** [X]hrs/week
                    **Expected Results:** [Key metrics]
                    **Pros:** [2 advantages]
                    **Cons:** [2 challenges]

                    REMEMBER: Only reference channels that exist in this list: {all_channels_str}

                    ---

                    After ALL 5 STRATEGIES, add:

                    ## RECOMMENDATION
                    **Best Strategy:** Strategy [number]
                    **Why:** [2-3 sentences]
                    **Week 1 Action Plan:** [3-5 steps]
                    """,
                    expected_output="Exactly 5 complete content strategies",
                    agent=strategy_architect,
                    context=[analyze_brand]
                )

                phase1_crew = Crew(
                    agents=[brand_analyst, strategy_architect],
                    tasks=[analyze_brand, generate_strategies],
                    process=Process.sequential,
                    verbose=False
                )

                st.write("🤖 AI agents working...")

                # Log Phase 1 start
                import time
                start_time = time.time()
                log_generation_start(data['brand_name'], "Phase 1: Strategy Generation")

                strategies_result = phase1_crew.kickoff()

                # Calculate duration
                duration = time.time() - start_time

                brand_analysis_output = str(analyze_brand.output)
                strategies_output = str(strategies_result)

                # STORE IN SESSION STATE
                st.session_state.brand_analysis_output = brand_analysis_output
                st.session_state.strategies_output = strategies_output
                st.session_state.analyze_brand_task = analyze_brand
                st.session_state.generate_strategies_task = generate_strategies
                st.session_state.strategies_generated = True

                # Save Phase 1 outputs
                with open("outputs/1_brand_analysis.md", "w", encoding="utf-8") as f:
                    f.write(brand_analysis_output)

                with open("outputs/2_five_strategies.md", "w", encoding="utf-8") as f:
                    f.write(strategies_output)

                # Log completion
                log_generation_complete(data['brand_name'], "Phase 1: Strategy Generation", duration)
                logger.info(f"Generated {len(strategies_output)} chars of strategy content")

                status1.update(label="✅ Phase 1 Complete! 5 strategies generated.", state="complete")

            except Exception as e:
                status1.update(label="❌ Phase 1 Failed", state="error")
                st.error(f"Error in Phase 1: {str(e)}")
                log_error(e, context={'phase': 'Phase 1', 'brand': data['brand_name']})
                st.stop()
    else:
        # Already generated - show cached result
        st.success("✅ Phase 1: Strategies already generated (using cached version)")

    # Display strategies
    st.markdown("### 📊 5 Strategy Options Generated!")

    with st.expander("📖 View All 5 Strategies", expanded=not st.session_state.calendar_generated):
        st.markdown(st.session_state.strategies_output)

    st.markdown("---")

    # Strategy selection
    if 'selected_strategy' not in st.session_state:
        st.session_state.selected_strategy = 1

    st.markdown("### 🎯 Select a Strategy to Expand")
    selected_strategy = st.radio(
        "Which strategy would you like to expand into a full content calendar?",
        options=[1, 2, 3, 4, 5],
        format_func=lambda x: f"Strategy {x}",
        horizontal=True,
        key="strategy_radio",
        index=st.session_state.selected_strategy - 1
    )

    # Update selection
    st.session_state.selected_strategy = selected_strategy

    if st.button("📅 Generate Calendar for Selected Strategy", type="primary", disabled=st.session_state.calendar_generated):
        st.session_state.calendar_generation = True
        st.rerun()

    # Phase 2: Content Calendar
    # ONLY RUN IF BUTTON CLICKED AND NOT ALREADY GENERATED
    if st.session_state.get('calendar_generation', False) and not st.session_state.calendar_generated:
        with st.status(f"📅 Phase 2: Creating content calendar for Strategy {st.session_state.selected_strategy}...", expanded=True) as status2:
            st.write("🔄 Generating 20-25 content pieces...")

            try:
                # Verify strategies were generated first
                if not st.session_state.strategies_generated:
                    st.error("Please generate strategies first")
                    st.session_state.calendar_generation = False
                    st.stop()

                # Get the stored outputs
                brand_analysis_output = st.session_state.brand_analysis_output
                strategies_output = st.session_state.strategies_output

                # Format channel distribution
                primary_channels_str = ', '.join(data.get('primary_channels', []))
                secondary_channels_str = ', '.join(data.get('secondary_channels', []))

                # Create brand analyst task for context
                analyze_brand_for_calendar = Task(
                    description=f"Brand context: {brand_data_text}",
                    expected_output="Brand context for calendar",
                    agent=brand_analyst
                )

                # Create strategy task for context
                strategies_for_calendar = Task(
                    description=f"Use these strategies as context: {strategies_output[:1000]}...\n\nFocus on Strategy {st.session_state.selected_strategy}.",
                    expected_output="Strategy context",
                    agent=strategy_architect,
                    context=[analyze_brand_for_calendar]
                )

                # Ensure we're using the correct brand name
                current_brand = data['brand_name']

                build_calendar = Task(
                    description=f"""
                    CRITICAL: You are creating content for the brand "{current_brand}" (not any other brand).

                    Create a detailed content calendar for {current_brand} in {data['strategy_month']}
                    based on Strategy {st.session_state.selected_strategy}.

                    Brand: {current_brand}
                    Industry: {data['industry']}

                    IMPORTANT: You must generate ALL 20-25 content pieces in a single response.
                    YOU MUST GENERATE EXACTLY 20-25 CONTENT PIECES. DO NOT STOP EARLY.

                    CRITICAL: All content must be relevant to {current_brand} and {data['industry']}.
                    Do NOT reference any other brand names like "Keka" or previous examples.
                    Every piece should be specifically tailored to {current_brand}.

                    CHANNEL DISTRIBUTION:
                    - Primary channels (60-70% of content): {primary_channels_str}
                    - Secondary channels (30-40% of content): {secondary_channels_str}
                    - Ensure content is distributed across ALL channels with variety
                    - Each piece should specify which specific channel it's for

                    For each content piece (numbered 1-25), provide:

                    **Content #[number]**
                    Week [1-4] | [Date] | **Title:** [Specific title - not generic]
                    Pillar: [Name] | Channel: [Platform] | Format: [Type]
                    Message: [One specific sentence - not placeholder]
                    CTA: [Specific action]
                    Effort: [L/M/H]

                    ---

                    After all 20-25 pieces, include:

                    ## EXECUTIVE SUMMARY
                    [2-3 sentences about the calendar strategy]

                    ## WEEKLY BREAKDOWN
                    **Week 1:** [Summary]
                    **Week 2:** [Summary]
                    **Week 3:** [Summary]
                    **Week 4:** [Summary]

                    ## CONTENT MIX
                    - By Format: [Breakdown]
                    - By Pillar: [Distribution]
                    - By Channel: [Distribution across all channels]

                    REMEMBER: Generate all 20-25 pieces before summaries. Use specific, detailed content - not placeholders.
                    """,
                    expected_output="Complete content calendar with 20-25 pieces",
                    agent=content_calendar_specialist,
                    context=[analyze_brand_for_calendar, strategies_for_calendar]
                )

                phase2_crew = Crew(
                    agents=[content_calendar_specialist],
                    tasks=[build_calendar],
                    process=Process.sequential,
                    verbose=False
                )

                st.write("🤖 AI creating your content calendar...")

                # Log Phase 2 start
                start_time = time.time()
                log_generation_start(current_brand, "Phase 2: Calendar Generation")

                calendar_result = phase2_crew.kickoff()

                # Calculate duration
                duration = time.time() - start_time

                calendar_output = str(calendar_result)

                # Validate brand name in output
                if 'keka' in calendar_output.lower() and 'keka' not in current_brand.lower():
                    st.warning(f"⚠️ AI generated content for wrong brand. Please regenerate...")
                    logger.warning("Brand validation failed - wrong brand in output", context={'expected': current_brand})
                    st.session_state.calendar_generated = False
                    st.session_state.calendar_generation = False
                    st.error("The AI referenced 'Keka' instead of your brand. Please click 'Generate Calendar' again to retry with correct brand.")
                    st.stop()

                st.write(f"✅ Calendar generated for {current_brand}")

                # Log completion
                log_generation_complete(current_brand, "Phase 2: Calendar Generation", duration)
                logger.info(f"Generated {len(calendar_output)} chars of calendar content")

                # Save Phase 2 output
                with open("outputs/3_content_calendar.md", "w", encoding="utf-8") as f:
                    f.write(calendar_output)

                st.session_state.calendar_output = calendar_output

                st.write("📄 Generating professional documents...")

                # Parse real AI content with error handling
                try:
                    parser = ContentCalendarParser()
                    parsed_calendar = parser.parse_calendar_output(calendar_output)
                    parsed_strategies = parse_strategies_output(st.session_state.strategies_output)

                    # Use real content pieces
                    real_content_pieces = parsed_calendar.get('content_pieces', [])

                    st.write(f"✅ Parsed {len(real_content_pieces)} content pieces from AI output")

                except Exception as parse_error:
                    st.warning(f"Parser error: {str(parse_error)}")
                    st.write("Using fallback content structure...")
                    log_error(parse_error, context={'phase': 'Parsing', 'brand': current_brand})

                    # Fallback to minimal structure
                    real_content_pieces = []
                    parsed_calendar = {'executive_summary': '', 'pillars': {}, 'success_metrics': []}
                    parsed_strategies = []

                # Ensure minimum 20 pieces
                if len(real_content_pieces) < 20:
                    st.warning(f"Only {len(real_content_pieces)} pieces parsed. Adding {20 - len(real_content_pieces)} placeholders...")

                    # Get primary channel for fallback
                    primary_channels = data.get('primary_channels', [data.get('primary_channel', 'LinkedIn')])
                    primary = primary_channels[0] if primary_channels else 'LinkedIn'

                    for i in range(len(real_content_pieces) + 1, 21):
                        real_content_pieces.append({
                            "content_id": i,
                            "week": (i-1)//5 + 1,
                            "suggested_date": f"{data['strategy_month'].split()[0]} {i}, 2025",
                            "title": f"Content Piece {i}",
                            "channel": primary,
                            "format": "Text Post",
                            "pillar": "Pillar 1",
                            "description": "Content description",
                            "key_message": "Key message",
                            "call_to_action": "Take action",
                            "effort_level": "Medium",
                            "effort_explanation": "Standard effort",
                            "engagement_potential": "Medium",
                            "engagement_reasoning": "Standard engagement",
                            "execution_notes": "Execution notes",
                            "seo_keyword": ""
                        })

                st.write(f"📊 Total content pieces: {len(real_content_pieces)}")

                # Use parsed strategies (with fallback)
                if len(parsed_strategies) < 5:
                    st.warning(f"Only {len(parsed_strategies)} strategies parsed. Using fallback data.")
                    # Add minimal fallback strategies
                    for i in range(len(parsed_strategies) + 1, 6):
                        parsed_strategies.append({
                            "strategy_number": i,
                            "name": f"Strategy {i}",
                            "tagline": f"Strategy {i} approach for {data['brand_name']}",
                            "core_approach": "Strategic content approach tailored to your brand",
                            "content_pillars": [
                                {"name": "Pillar 1", "description": "First content pillar"},
                                {"name": "Pillar 2", "description": "Second content pillar"},
                                {"name": "Pillar 3", "description": "Third content pillar"},
                            ],
                            "posting_frequency": {},
                            "content_mix": {},
                            "top_5_ideas": [f"Content idea {j}" for j in range(1, 6)],
                            "pros": ["Effective approach", "Scalable"],
                            "cons": ["Requires consistency"]
                        })

                # Generate documents with individual error handling
                logger.info("Starting document generation", context={'brand': current_brand})

                try:
                    generate_strategy_docx(
                        brand_name=data['brand_name'],
                        strategies_list=parsed_strategies[:5] if parsed_strategies else [],
                        recommendation=f"Strategy {st.session_state.selected_strategy} recommended based on analysis",
                        output_path="outputs/strategy_options.docx"
                    )
                    st.write("✅ Strategy DOCX generated")
                    logger.info("Strategy DOCX generated successfully")
                except Exception as docx_error:
                    st.error(f"Strategy DOCX error: {str(docx_error)}")
                    log_error(docx_error, context={'document': 'Strategy DOCX', 'brand': current_brand})

                try:
                    generate_calendar_docx(
                        brand_name=data['brand_name'],
                        strategy_name=f"Strategy {st.session_state.selected_strategy}",
                        month=data['strategy_month'],
                        executive_summary=parsed_calendar.get('executive_summary', 'This content calendar brings your strategy to life with actionable content pieces.'),
                        content_pieces=real_content_pieces,
                        output_path="outputs/content_calendar.docx"
                    )
                    st.write("✅ Calendar DOCX generated")
                    logger.info("Calendar DOCX generated successfully")
                except Exception as cal_docx_error:
                    st.error(f"Calendar DOCX error: {str(cal_docx_error)}")
                    log_error(cal_docx_error, context={'document': 'Calendar DOCX', 'brand': current_brand})

                try:
                    # Use parsed success metrics or fallback
                    success_metrics = parsed_calendar.get('success_metrics', [
                        "Engagement rate > 3%",
                        "50+ qualified leads per month",
                        "Website traffic increase of 25%",
                        "Social follower growth of 15%"
                    ])

                    generate_content_calendar_xlsx(
                        brand_name=data['brand_name'],
                        month=data['strategy_month'],
                        content_pieces=real_content_pieces,
                        success_metrics=success_metrics,
                        output_path="outputs/content_calendar.xlsx"
                    )
                    st.write("✅ Calendar XLSX generated")
                    logger.info("Calendar XLSX generated successfully")
                except Exception as xlsx_error:
                    st.error(f"Calendar XLSX error: {str(xlsx_error)}")
                    log_error(xlsx_error, context={'document': 'Calendar XLSX', 'brand': current_brand})

                # Save structured outputs
                outputs = {
                    "brand_analysis": st.session_state.brand_analysis_output,
                    "strategies": st.session_state.strategies_output,
                    "selected_strategy": st.session_state.selected_strategy,
                    "calendar": calendar_output,
                    "brand_info": data
                }

                with open("outputs/streamlit_output.json", "w", encoding="utf-8") as f:
                    json.dump(outputs, f, indent=2, ensure_ascii=False)

                with open("outputs/streamlit_output.yaml", "w", encoding="utf-8") as f:
                    yaml.dump(outputs, f, default_flow_style=False, allow_unicode=True)

                # Mark workflow as complete
                st.session_state.workflow_complete = True
                st.session_state.calendar_generated = True
                st.session_state.calendar_generation = False

                logger.info("Workflow completed successfully", context={'brand': current_brand})
                log_user_action("Workflow completed", {'brand': current_brand, 'strategy': st.session_state.selected_strategy})

                status2.update(label="✅ Phase 2 Complete! Content calendar generated.", state="complete")

            except Exception as e:
                status2.update(label="❌ Phase 2 Failed", state="error")
                st.error(f"Error in Phase 2: {str(e)}")
                log_error(e, context={'phase': 'Phase 2', 'brand': current_brand})
                st.session_state.calendar_generation = False
                st.stop()

    # Show download buttons if workflow is complete
    if st.session_state.calendar_generated:
        st.markdown("---")
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("## 🎉 Success! Your Content Strategy is Ready!")
        st.markdown(f"### {data['brand_name']} - {data['strategy_month']}")
        st.markdown("</div>", unsafe_allow_html=True)

        # Download buttons
        st.markdown("### 📥 Download Your Strategy Files")

        col1, col2, col3 = st.columns(3)

        with col1:
            try:
                with open("outputs/strategy_options.docx", "rb") as f:
                    st.download_button(
                        label="📄 Strategy Options (DOCX)",
                        data=f,
                        file_name=f"{data['brand_name']}_strategies.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        key="download_strategies"
                    )
            except FileNotFoundError:
                st.error("Strategy file not found")

        with col2:
            try:
                with open("outputs/content_calendar.docx", "rb") as f:
                    st.download_button(
                        label="📄 Content Calendar (DOCX)",
                        data=f,
                        file_name=f"{data['brand_name']}_calendar.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        key="download_calendar_docx"
                    )
            except FileNotFoundError:
                st.error("Calendar DOCX not found")

        with col3:
            try:
                with open("outputs/content_calendar.xlsx", "rb") as f:
                    st.download_button(
                        label="📊 Calendar Spreadsheet (XLSX)",
                        data=f,
                        file_name=f"{data['brand_name']}_calendar.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key="download_calendar_xlsx"
                    )
            except FileNotFoundError:
                st.error("Calendar XLSX not found")

        # Display calendar preview
        st.markdown("---")
        st.markdown("### 📋 Content Calendar Preview")
        with st.expander("View Your Content Calendar", expanded=False):
            st.markdown(st.session_state.calendar_output)

        st.markdown("---")

        if st.button("🔄 Generate Strategy for Another Brand", type="primary", use_container_width=True):
            reset_workflow()
            st.rerun()

if __name__ == "__main__":
    if st.session_state.step == 1:
        st.markdown("### Welcome! Let's create your AI-powered content strategy.")
        st.markdown("Complete the 8-step questionnaire to get started.")
