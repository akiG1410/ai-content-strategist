# -*- coding: utf-8 -*-
import os
import json
import yaml
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv
from document_generator import generate_strategy_docx, generate_calendar_docx
from excel_generator import generate_content_calendar_xlsx

# Load environment variables
load_dotenv()

# Configure LLM to use OpenRouter with LiteLLM provider
llm = LLM(
    model="openai/anthropic/claude-3.5-sonnet",
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

def display_strategy_summary(strategies_output):
    """Display a clean summary of all 5 strategies"""
    print("\n" + "="*70)
    print("📊 STRATEGY OPTIONS SUMMARY")
    print("="*70 + "\n")

    # Display the strategies
    print(strategies_output)
    print("\n" + "="*70)

def get_user_strategy_choice():
    """Get user's strategy selection with validation"""
    while True:
        try:
            choice = input("\n👉 Which strategy would you like to expand into a full content calendar? (1-5): ").strip()
            choice_num = int(choice)
            if 1 <= choice_num <= 5:
                return choice_num
            else:
                print("❌ Please enter a number between 1 and 5")
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\n❌ Workflow cancelled by user")
            exit(0)

def parse_strategies_for_docx(strategies_text):
    """
    Parse the strategy text into structured data for DOCX generation.
    This is a simple parser - in production you'd use structured output from agents.
    """
    # For now, return mock structured data
    # In the next enhancement, we'll use proper Pydantic models
    strategies = []
    for i in range(1, 6):
        strategies.append({
            "name": f"Strategy {i}",
            "tagline": f"Approach {i} tagline",
            "core_approach": "Strategic approach description",
            "content_pillars": [
                {"name": "Pillar 1", "description": "Description"},
                {"name": "Pillar 2", "description": "Description"},
            ],
            "posting_frequency": {"LinkedIn": "3x/week", "Twitter": "5x/week"},
            "content_mix": {"Educational": 60, "Promotional": 20, "Engagement": 20},
            "top_5_ideas": [f"Content idea {j}" for j in range(1, 6)],
            "expected_results": ["Result 1", "Result 2"],
            "pros": ["Pro 1", "Pro 2", "Pro 3"],
            "cons": ["Con 1", "Con 2"]
        })
    return strategies

def run_interactive_workflow():
    """Run the workflow with interactive strategy selection"""

    print("\n" + "="*70)
    print("🚀 AI CONTENT MARKETING STRATEGIST - INTERACTIVE MODE")
    print("="*70 + "\n")

    # Create agents
    brand_analyst = Agent(
        role="Senior Brand Analyst",
        goal="Deeply understand the brand's context, audience, and competitive position to inform strategy",
        backstory="""You're a veteran brand strategist with 15 years of experience analyzing
                     businesses across industries. You have a talent for finding the unique
                     angles that make brands stand out.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    strategy_architect = Agent(
        role="Chief Content Strategy Architect",
        goal="Create 5 distinct, actionable content strategies tailored to the brand's unique situation",
        backstory="""You're a renowned content strategist who has developed award-winning
                     campaigns for Fortune 500 companies and scrappy startups alike. You
                     always complete your full assignment - if asked for 5 strategies, you deliver all 5.""",
        verbose=True,
        allow_delegation=False,
        max_iter=25,
        llm=llm
    )

    content_calendar_specialist = Agent(
        role="Content Calendar Specialist",
        goal="Transform a chosen strategy into a detailed, executable 20-25 piece content calendar",
        backstory="""You're the person everyone calls when they need a content plan that
                     actually gets executed. You create calendars that are specific, actionable, and realistic.
                     You never use vague titles like "Create engaging post" - you write actual
                     content titles that could be published as-is.""",
        verbose=True,
        allow_delegation=False,
        max_iter=35,
        llm=llm
    )

    # PHASE 1: Brand Analysis + Strategy Generation
    print("📋 PHASE 1: Analyzing brand and generating 5 strategy options...")
    print("   This will take about 90-120 seconds...\n")

    analyze_brand = Task(
        description=f"""
        Analyze the following brand information and create a comprehensive brand profile:

        {brand_data}

        Your analysis should include:
        1. Brand Positioning Summary (2-3 sentences)
        2. Primary Audience Characteristics
        3. Key Differentiators
        4. Content Opportunities
        5. Channel-Specific Considerations
        6. Constraints & Resources
        7. Strategic Imperatives
        8. Competitive Gaps

        Be specific and insightful.
        """,
        expected_output="A comprehensive brand analysis document",
        agent=brand_analyst
    )

    generate_strategies = Task(
        description="""
        IMPORTANT: You must generate ALL 5 strategies in a single response.

        Based on the brand analysis you received, create 5 COMPLETE AND DISTINCT content strategy options.

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

        After ALL 5 COMPLETE STRATEGIES, add:

        ## RECOMMENDATION
        **Best Strategy for CloudFlow:** Strategy [number]
        **Why:** [2-3 sentences explaining why this specific strategy fits best]
        **Week 1 Action Plan:** [3-5 specific steps to get started]
        """,
        expected_output="Exactly 5 complete, distinct content strategy options",
        agent=strategy_architect,
        context=[analyze_brand]
    )

    phase1_crew = Crew(
        agents=[brand_analyst, strategy_architect],
        tasks=[analyze_brand, generate_strategies],
        process=Process.sequential,
        verbose=True
    )

    strategies_result = phase1_crew.kickoff()

    # Save Phase 1 outputs
    brand_analysis_output = analyze_brand.output.raw if hasattr(analyze_brand.output, 'raw') else str(analyze_brand.output)
    strategies_output = str(strategies_result)

    with open("outputs/1_brand_analysis.md", "w", encoding="utf-8") as f:
        f.write(brand_analysis_output)

    with open("outputs/2_five_strategies.md", "w", encoding="utf-8") as f:
        f.write(strategies_output)

    print("\n✅ Phase 1 Complete!")
    print("   - Brand analysis saved to outputs/1_brand_analysis.md")
    print("   - 5 strategies saved to outputs/2_five_strategies.md")

    # Display strategies and get user choice
    display_strategy_summary(strategies_output)

    selected_strategy = get_user_strategy_choice()

    print(f"\n✅ You selected Strategy {selected_strategy}")
    print(f"   Generating detailed content calendar...\n")

    # PHASE 2: Content Calendar for Selected Strategy
    print("📅 PHASE 2: Creating detailed content calendar...")
    print("   This will take about 60-90 seconds...\n")

    # Create new calendar task with the selected strategy
    build_calendar_interactive = Task(
        description=f"""
        IMPORTANT: You must generate ALL 20-25 content pieces in a single response.

        Create a detailed content calendar for January 2025 based on Strategy {selected_strategy}
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

        REMEMBER: Generate all 20-25 pieces before moving to the summary sections.
        """,
        expected_output="Complete content calendar with 20-25 pieces",
        agent=content_calendar_specialist,
        context=[analyze_brand, generate_strategies]
    )

    phase2_crew = Crew(
        agents=[content_calendar_specialist],
        tasks=[build_calendar_interactive],
        process=Process.sequential,
        verbose=True
    )

    calendar_result = phase2_crew.kickoff()

    # Save Phase 2 outputs
    calendar_output = str(calendar_result)

    with open("outputs/3_content_calendar.md", "w", encoding="utf-8") as f:
        f.write(calendar_output)

    # Create comprehensive package
    comprehensive_output = f"""# AI Content Marketing Strategy - Complete Report
Generated: January 2025
Brand: CloudFlow
Selected Strategy: #{selected_strategy} (User Choice - Interactive Mode)

---

# PART 1: BRAND ANALYSIS

{brand_analysis_output}

---

# PART 2: STRATEGY OPTIONS (5 Complete Strategies)

{strategies_output}

---

# PART 3: CONTENT CALENDAR (Strategy {selected_strategy})

{calendar_output}

---

## SELECTION SUMMARY

✅ Strategy Selected: #{selected_strategy}
✅ Selection Method: Interactive user choice
✅ Calendar Generated: 20-25 pieces for January 2025

---

*Generated by AI Content Marketing Strategist (CrewAI) - Interactive Mode*
"""

    with open("outputs/complete_strategy_package_interactive.md", "w", encoding="utf-8") as f:
        f.write(comprehensive_output)

    # Save as JSON/YAML too
    outputs = {
        "brand_analysis": brand_analysis_output,
        "strategies": strategies_output,
        "selected_strategy": selected_strategy,
        "calendar": calendar_output
    }

    with open("outputs/interactive_output.json", "w", encoding="utf-8") as f:
        json.dump(outputs, f, indent=2, ensure_ascii=False)

    with open("outputs/interactive_output.yaml", "w", encoding="utf-8") as f:
        yaml.dump(outputs, f, default_flow_style=False, allow_unicode=True)

    # Generate DOCX documents
    print("\n📄 Generating professional documents...")

    # Generate Strategy Options DOCX
    try:
        strategies_structured = parse_strategies_for_docx(strategies_output)
        strategy_docx_path = generate_strategy_docx(
            brand_name="CloudFlow",
            strategies_list=strategies_structured,
            recommendation=f"We recommend Strategy {selected_strategy} based on your analysis.",
            output_path="outputs/strategy_options.docx"
        )
        print(f"   ✅ Strategy options document: {strategy_docx_path}")
    except Exception as e:
        print(f"   ⚠️  Strategy DOCX generation failed: {str(e)}")

    # Generate Calendar DOCX (simplified for now)
    try:
        # Mock calendar data for now
        mock_content_pieces = []
        for i in range(1, 21):
            mock_content_pieces.append({
                "content_id": i,
                "week": (i-1)//5 + 1,
                "suggested_date": f"January {i}, 2025",
                "title": f"Content Piece {i}",
                "channel": "LinkedIn",
                "format": "Text Post",
                "pillar": "Pillar 1",
                "description": "Content description here",
                "key_message": "Key message",
                "call_to_action": "Take action",
                "effort_level": "Medium",
                "engagement_potential": "High",
                "execution_notes": "How to create this"
            })

        calendar_docx_path = generate_calendar_docx(
            brand_name="CloudFlow",
            strategy_name=f"Strategy {selected_strategy}",
            month="January 2025",
            executive_summary="This calendar brings your strategy to life with 20 pieces of content.",
            content_pieces=mock_content_pieces,
            output_path="outputs/content_calendar.docx"
        )
        print(f"   ✅ Content calendar document: {calendar_docx_path}")
    except Exception as e:
        print(f"   ⚠️  Calendar DOCX generation failed: {str(e)}")

    # Generate Calendar XLSX
    try:
        success_metrics = [
            "Engagement rate > 3%",
            "50+ qualified leads per month",
            "Website traffic increase of 25%",
            "Social follower growth of 15%"
        ]

        xlsx_path = generate_content_calendar_xlsx(
            brand_name="CloudFlow",
            month="January 2025",
            content_pieces=mock_content_pieces,
            success_metrics=success_metrics,
            output_path="outputs/content_calendar.xlsx"
        )
        print(f"   ✅ Content calendar spreadsheet: {xlsx_path}")
    except Exception as e:
        print(f"   ⚠️  XLSX generation failed: {str(e)}")

    # Final summary
    print("\n" + "="*70)
    print("✅ WORKFLOW COMPLETE!")
    print("="*70)
    print(f"\n📊 Summary:")
    print(f"   ✅ Brand analyzed")
    print(f"   ✅ 5 strategies generated")
    print(f"   ✅ Strategy {selected_strategy} selected (your choice)")
    print(f"   ✅ Content calendar created (20+ pieces)")
    print(f"\n📁 Output files:")
    print(f"   - outputs/complete_strategy_package_interactive.md (everything)")
    print(f"   - outputs/strategy_options.docx (5 strategies) ⭐")
    print(f"   - outputs/content_calendar.docx (calendar) ⭐")
    print(f"   - outputs/content_calendar.xlsx (Excel - 4 tabs) ⭐")
    print(f"   - outputs/1_brand_analysis.md")
    print(f"   - outputs/2_five_strategies.md")
    print(f"   - outputs/3_content_calendar.md")
    print(f"   - outputs/interactive_output.json")
    print(f"   - outputs/interactive_output.yaml")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_interactive_workflow()
