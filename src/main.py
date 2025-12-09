# -*- coding: utf-8 -*-
import os
import json
import yaml
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from models import BrandAnalysis, StrategiesOutput, ContentCalendar

# Load environment variables
load_dotenv()

# Helper function to save structured outputs in multiple formats
def save_structured_outputs(brand_analysis_obj, strategies_obj, calendar_obj):
    """Save outputs in multiple structured formats (JSON and YAML)"""

    # Prepare data for JSON/YAML export
    outputs = {}

    if brand_analysis_obj:
        outputs["brand_analysis"] = brand_analysis_obj.dict()

    if strategies_obj:
        outputs["strategies"] = strategies_obj.dict()

    if calendar_obj:
        outputs["calendar"] = calendar_obj.dict()

    # Save as JSON
    with open("outputs/structured_output.json", "w", encoding="utf-8") as f:
        json.dump(outputs, f, indent=2, ensure_ascii=False)

    # Save as YAML (more human-readable)
    with open("outputs/structured_output.yaml", "w", encoding="utf-8") as f:
        yaml.dump(outputs, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print("   - outputs/structured_output.json (all combined)")
    print("   - outputs/structured_output.yaml (all combined)")

# Configure LLM to use OpenRouter with ChatOpenAI
llm = ChatOpenAI(
    model="anthropic/claude-sonnet-4-5-20250929",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0.7
)

# Sample brand data for testing
brand_data = """
Brand Name: CloudFlow
Industry: B2B SaaS - Project Management
Target Audience: Marketing teams at mid-size companies (50-500 employees) who need
                 better project management and collaboration tools. They're frustrated
                 with disjointed workflows and spending too much time in meetings.
Business Goals: Brand Awareness, Lead Generation, Product Education
Active Channels: LinkedIn, Twitter, Blog
Primary Channel: LinkedIn
Brand Tone: Professional yet approachable
Monthly Budget: $2,500 - $5,000
Weekly Time Commitment: 10-20 hours
Unique Value Proposition: AI-powered project management that automatically prioritizes
                          tasks and suggests optimal workflows
Key Products: Project management platform, Team collaboration suite, AI task prioritization
Strategy Month: January 2025
Additional Notes: Launching new AI feature next month - want to generate buzz
"""

# For this workflow, we'll generate a calendar for Strategy 1
selected_strategy_number = 1

# AGENT 1: Brand Analyst
brand_analyst = Agent(
    role="Senior Brand Analyst",
    goal="Deeply understand the brand's context, audience, and competitive position to inform strategy",
    backstory="""You're a veteran brand strategist with 15 years of experience analyzing
                 businesses across industries. You have a talent for finding the unique
                 angles that make brands stand out. You ask probing questions and identify
                 opportunities others miss. You're known for spotting the "hidden gems" -
                 unique positioning opportunities that competitors haven't claimed yet.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# AGENT 2: Strategy Architect
strategy_architect = Agent(
    role="Chief Content Strategy Architect",
    goal="Create 5 distinct, actionable content strategies tailored to the brand's unique situation",
    backstory="""You're a renowned content strategist who has developed award-winning
                 campaigns for Fortune 500 companies and scrappy startups alike. You
                 believe every brand deserves a strategy that feels custom-built, not
                 generic. You never create two identical strategies. You always provide
                 specific, actionable ideas - never generic advice. You always complete
                 your full assignment - if asked for 5 strategies, you deliver all 5.""",
    verbose=True,
    allow_delegation=False,
    max_iter=25,  # Allow more iterations to complete all 5 strategies
    llm=llm
)

# AGENT 3: Content Calendar Specialist
content_calendar_specialist = Agent(
    role="Content Calendar Specialist",
    goal="Transform a chosen strategy into a detailed, executable 20-25 piece content calendar",
    backstory="""You're the person everyone calls when they need a content plan that
                 actually gets executed. You've managed content calendars for brands
                 publishing 100+ pieces per month. You know exactly what information
                 content creators need to do their jobs without asking follow-up questions.
                 You create calendars that are specific, actionable, and realistic. You
                 never use vague titles like "Create engaging post" - you write actual
                 content titles that could be published as-is.""",
    verbose=True,
    allow_delegation=False,
    max_iter=35,  # Allow enough iterations for 20-25 content pieces
    llm=llm
)

# TASK 1: Analyze Brand Context
analyze_brand = Task(
    description=f"""
    Analyze the following brand information and create a comprehensive brand profile:

    {brand_data}

    Your analysis should include:

    1. **Brand Positioning Summary** (2-3 sentences)
       - What makes this brand unique in their market?
       - What's their core promise to customers?

    2. **Primary Audience Characteristics**
       - Who are they exactly?
       - What are their key pain points?
       - What motivates them?

    3. **Key Differentiators**
       - What sets them apart from competitors?
       - What can they own that others can't?

    4. **Content Opportunities**
       - Based on their goals, what content angles will work best?
       - What topics should they focus on?

    5. **Channel-Specific Considerations**
       - Which channels match their audience best?
       - What content types work on each channel?

    6. **Constraints & Resources**
       - Budget limitations
       - Time availability
       - Team capabilities

    7. **Strategic Imperatives**
       - What MUST the content achieve?
       - What would success look like in 30 days?

    8. **Competitive Gaps**
       - What are competitors NOT talking about?
       - Where's the white space in the conversation?

    Be specific and insightful. Don't just repeat the input - synthesize it into actionable intelligence.

    Output the analysis as a structured JSON object with these fields:
    - brand_positioning (string)
    - target_audience (string)
    - key_differentiators (list of strings)
    - content_opportunities (list of strings)
    - constraints (dict with budget, time, resources keys)
    - strategic_imperatives (list of strings)
    - competitive_gaps (list of strings)
    """,
    expected_output="A comprehensive brand analysis document with clear insights and strategic recommendations",
    agent=brand_analyst,
    output_pydantic=BrandAnalysis
)

# TASK 2: Generate Strategy Options (now with stronger completion requirements)
generate_strategies = Task(
    description="""
    IMPORTANT: You must generate ALL 5 strategies in a single response. Do not ask for permission to continue.
    Complete the entire task without stopping.

    Based on the brand analysis you received, create 5 COMPLETE AND DISTINCT content strategy options.

    YOU MUST GENERATE ALL 5 STRATEGIES BEFORE FINISHING. DO NOT STOP AFTER 1 OR 2. DO NOT ASK IF YOU SHOULD CONTINUE.

    CRITICAL REQUIREMENTS:
    - Generate EXACTLY 5 strategies (Strategy 1, Strategy 2, Strategy 3, Strategy 4, Strategy 5)
    - Each strategy must be FUNDAMENTALLY DIFFERENT in approach
    - No two strategies should feel like variations of the same idea
    - Each must address the specific insights from the brand analysis
    - Consider the brand's constraints (budget, time, resources)

    For EACH of the 5 strategies, provide (keep it concise):

    **Strategy [NUMBER]: [Name]**
    **Tagline:** One memorable sentence
    **Core Approach:** 2-3 sentences
    **Why This Strategy:** 1-2 sentences
    **Content Pillars:** Pillar 1 | Pillar 2 | Pillar 3
    **Posting Frequency:** LinkedIn [X]/week, Twitter [X]/week, Blog [X]/month
    **Content Mix:** Educational [X]%, Promotional [X]%, Engagement [X]%, Curated [X]%
    **Top 3 Content Ideas:**
      1. [Title]
      2. [Title]
      3. [Title]
    **Effort:** [X]hrs/week, Resources: [brief list]
    **30-Day Results:** [Key metrics]
    **Pros:** [2 key advantages]
    **Cons:** [2 key challenges with brief mitigations]

    ---

    Strategy Archetypes you MUST cover (pick 5 different ones):
    1. Thought Leadership - Position as industry expert
    2. Community Building - Focus on engagement and conversation
    3. Educational Hub - Become the go-to learning resource
    4. Product-Led Growth - Let the product speak through content
    5. Customer Stories - Let customers be the heroes
    6. Trend Riding - Capitalize on industry momentum
    7. Data & Research - Original insights that get shared

    After ALL 5 COMPLETE STRATEGIES, add:

    ## RECOMMENDATION
    **Best Strategy for CloudFlow:** Strategy [number]
    **Why:** [2-3 sentences explaining why this specific strategy fits best]
    **Week 1 Action Plan:** [3-5 specific steps to get started]

    REMEMBER: You must complete ALL 5 strategies before moving to the recommendation. Do not stop early.

    Output as a structured JSON object with:
    - strategies: list of 5 strategy objects, each with all required fields
    - recommendation: object with recommended_strategy_number, reasoning, and week_1_actions list
    """,
    expected_output="Exactly 5 complete, distinct content strategy options (numbered 1-5) that directly address the brand analysis, followed by a clear recommendation section",
    agent=strategy_architect,
    context=[analyze_brand],  # This is the key! Uses output from Task 1
    output_pydantic=StrategiesOutput
)

# TASK 3: Build Content Calendar
build_calendar = Task(
    description=f"""
    IMPORTANT: You must generate ALL 20-25 content pieces in a single response. Do not ask for permission to continue.
    Complete the entire task without stopping.

    Create a detailed content calendar for January 2025 based on Strategy {selected_strategy_number}
    from the strategies that were just generated.

    YOU MUST GENERATE EXACTLY 20-25 CONTENT PIECES. DO NOT STOP EARLY.

    For each content piece (numbered 1-25), provide (keep concise):

    **Content #[number]**
    Week [1-4] | [Date] | **Title:** [Specific title]
    Pillar: [Name] | Channel: [Platform] | Format: [Type]
    Message: [One sentence]
    CTA: [Specific action]
    Effort: [L/M/H]

    ---

    After all 20-25 content pieces, include:

    ## EXECUTIVE SUMMARY
    [2-3 sentences about the overall calendar strategy]

    ## WEEKLY BREAKDOWN
    **Week 1 (Jan 1-7):** [Summary]
    **Week 2 (Jan 8-14):** [Summary]
    **Week 3 (Jan 15-21):** [Summary]
    **Week 4 (Jan 22-31):** [Summary]

    ## CONTENT MIX
    - By Format: [Breakdown]
    - By Pillar: [Distribution]
    - By Channel: [Distribution]

    ## QUICK WINS
    [3 pieces that are easy to create and high impact - list content #s]

    REMEMBER: Generate all 20-25 pieces before moving to the summary sections. Keep each piece concise.

    Output as a structured JSON object with:
    - executive_summary: string
    - content_pieces: list of 20-25 content piece objects with all required fields
    - weekly_breakdown: dict with keys Week1, Week2, Week3, Week4
    - content_mix_analysis: dict with format, pillar, and channel breakdowns
    - success_metrics: list of KPIs to track
    - quick_wins: list of content IDs (integers)
    - production_notes: string describing resources needed
    """,
    expected_output="A complete content calendar with 20-25 specific content pieces and supporting analysis",
    agent=content_calendar_specialist,
    context=[analyze_brand, generate_strategies],  # Uses outputs from both previous tasks
    output_pydantic=ContentCalendar
)

# Create the crew with all three agents
crew = Crew(
    agents=[brand_analyst, strategy_architect, content_calendar_specialist],
    tasks=[analyze_brand, generate_strategies, build_calendar],
    process=Process.sequential,  # Tasks run in order
    verbose=True
)

# Main execution
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Starting Full Content Strategy Workflow...")
    print(f"   Generating calendar for Strategy {selected_strategy_number}")
    print("="*60 + "\n")

    try:
        # Run the full crew workflow
        result = crew.kickoff()

        print("\n" + "="*60)
        print("FULL WORKFLOW COMPLETE!")
        print("="*60 + "\n")

        # Access individual task outputs (now as Pydantic objects)
        brand_analysis_obj = analyze_brand.output.pydantic if hasattr(analyze_brand.output, 'pydantic') else None
        strategies_obj = generate_strategies.output.pydantic if hasattr(generate_strategies.output, 'pydantic') else None
        calendar_obj = result.pydantic if hasattr(result, 'pydantic') else None

        # Also get raw text outputs for markdown
        brand_analysis_output = analyze_brand.output.raw if hasattr(analyze_brand.output, 'raw') else str(analyze_brand.output)
        strategies_output = generate_strategies.output.raw if hasattr(generate_strategies.output, 'raw') else str(generate_strategies.output)
        calendar_output = result.raw if hasattr(result, 'raw') else str(result)

        # Create comprehensive document with all outputs
        comprehensive_output = f"""# AI Content Marketing Strategy - Complete Report
Generated: January 2025
Brand: CloudFlow

---

# PART 1: BRAND ANALYSIS

{brand_analysis_output}

---

# PART 2: STRATEGY OPTIONS (5 Complete Strategies)

{strategies_output}

---

# PART 3: CONTENT CALENDAR (Strategy {selected_strategy_number})

{calendar_output}

---

## DELIVERABLES SUMMARY

✅ Brand Analysis: Complete
✅ 5 Strategy Options: Generated
✅ Selected Strategy: #{selected_strategy_number}
✅ Content Calendar: 20-25 pieces for January 2025
✅ Execution Support: Weekly breakdowns, quick wins, success metrics

---

*Generated by AI Content Marketing Strategist (CrewAI)*
"""

        # Save comprehensive document
        output_path = "outputs/complete_strategy_package.md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(comprehensive_output)

        print(f"\nComplete strategy package saved to {output_path}")

        # Also save individual components for reference
        with open("outputs/1_brand_analysis.md", "w", encoding="utf-8") as f:
            f.write(brand_analysis_output)

        with open("outputs/2_five_strategies.md", "w", encoding="utf-8") as f:
            f.write(strategies_output)

        with open("outputs/3_content_calendar.md", "w", encoding="utf-8") as f:
            f.write(str(calendar_output))

        print("Individual components also saved:")
        print("   - outputs/1_brand_analysis.md")
        print("   - outputs/2_five_strategies.md")
        print("   - outputs/3_content_calendar.md")

        # Save structured JSON outputs if Pydantic objects are available
        if brand_analysis_obj:
            with open("outputs/1_brand_analysis.json", "w", encoding="utf-8") as f:
                json.dump(brand_analysis_obj.dict(), f, indent=2)
            print("   - outputs/1_brand_analysis.json (structured)")

        if strategies_obj:
            with open("outputs/2_five_strategies.json", "w", encoding="utf-8") as f:
                json.dump(strategies_obj.dict(), f, indent=2)
            print("   - outputs/2_five_strategies.json (structured)")

        if calendar_obj:
            with open("outputs/3_content_calendar.json", "w", encoding="utf-8") as f:
                json.dump(calendar_obj.dict(), f, indent=2)
            print("   - outputs/3_content_calendar.json (structured)")

        # Save combined structured outputs in JSON and YAML
        if brand_analysis_obj or strategies_obj or calendar_obj:
            save_structured_outputs(brand_analysis_obj, strategies_obj, calendar_obj)

        # Print summary
        print("\n" + "="*60)
        print("WORKFLOW SUMMARY")
        print("="*60)
        print(f"Brand analyzed")
        print(f"5 strategies generated")
        print(f"Strategy {selected_strategy_number} selected")
        print(f"Content calendar created")
        print(f"All outputs saved to outputs/ directory")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check that your OPENROUTER_API_KEY is set in .env")
        print("2. Verify you have credits in your OpenRouter account")
        print("3. This workflow takes 2-3 minutes - be patient!")
        import traceback
        traceback.print_exc()
