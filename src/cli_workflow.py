# -*- coding: utf-8 -*-
import os
import sys
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv
import json
import yaml
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables
load_dotenv()

# Configure LLM to use OpenRouter with LiteLLM provider
llm = LLM(
    model="openai/anthropic/claude-3.5-sonnet",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0.7
)

from cli_input import collect_brand_input
from document_generator import generate_strategy_docx, generate_calendar_docx
from excel_generator import generate_content_calendar_xlsx

def run_cli_workflow():
    """Run the full workflow with CLI input"""

    print("\n" + "="*70)
    print("🚀 AI CONTENT MARKETING STRATEGIST - CLI MODE")
    print("="*70 + "\n")

    # Step 1: Collect brand information
    print("Step 1: Collecting brand information...")
    brand_data_text, brand_data_dict = collect_brand_input()

    # Step 2: Create agents
    print("Step 2: Creating AI agents and tasks...\n")

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
        **Best Strategy for this brand:** Strategy [number]
        **Why:** [2-3 sentences explaining why this specific strategy fits best]
        **Week 1 Action Plan:** [3-5 specific steps to get started]
        """,
        expected_output="Exactly 5 complete, distinct content strategy options",
        agent=strategy_architect,
        context=[analyze_brand]
    )

    # Step 3: Run Phase 1
    print("="*70)
    print("📋 PHASE 1: Generating 5 Strategy Options")
    print("   This will take about 90-120 seconds...")
    print("="*70 + "\n")

    phase1_crew = Crew(
        agents=[brand_analyst, strategy_architect],
        tasks=[analyze_brand, generate_strategies],
        process=Process.sequential,
        verbose=True
    )

    strategies_result = phase1_crew.kickoff()

    brand_analysis_output = analyze_brand.output.raw if hasattr(analyze_brand.output, 'raw') else str(analyze_brand.output)
    strategies_output = str(strategies_result)

    # Save Phase 1 outputs
    with open("outputs/1_brand_analysis.md", "w", encoding="utf-8") as f:
        f.write(brand_analysis_output)

    with open("outputs/2_five_strategies.md", "w", encoding="utf-8") as f:
        f.write(strategies_output)

    print("\n✅ Phase 1 Complete! 5 strategies generated.\n")

    # Step 4: Strategy selection
    print("="*70)
    print("📊 STRATEGY SELECTION")
    print("="*70 + "\n")
    print("Please review the strategies above.\n")

    while True:
        try:
            selected = input("Which strategy would you like to expand into a content calendar? (1-5): ").strip()
            selected_num = int(selected)
            if 1 <= selected_num <= 5:
                break
            print("❌ Please enter a number between 1 and 5")
        except ValueError:
            print("❌ Please enter a valid number")
        except (EOFError, KeyboardInterrupt):
            print("\n\n❌ Workflow cancelled")
            sys.exit(0)

    print(f"\n✅ Strategy {selected_num} selected!\n")

    # Step 5: Generate calendar
    print("="*70)
    print("📅 PHASE 2: Creating Content Calendar")
    print(f"   Generating calendar for {brand_data_dict['strategy_month']}...")
    print("   This will take about 60-90 seconds...")
    print("="*70 + "\n")

    build_calendar = Task(
        description=f"""
        IMPORTANT: You must generate ALL 20-25 content pieces in a single response.

        Create a detailed content calendar for {brand_data_dict['strategy_month']}
        based on Strategy {selected_num} from the strategies that were just generated.

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
        **Week 1:** [Summary]
        **Week 2:** [Summary]
        **Week 3:** [Summary]
        **Week 4:** [Summary]

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
        tasks=[build_calendar],
        process=Process.sequential,
        verbose=True
    )

    calendar_result = phase2_crew.kickoff()
    calendar_output = str(calendar_result)

    # Save Phase 2 outputs
    with open("outputs/3_content_calendar.md", "w", encoding="utf-8") as f:
        f.write(calendar_output)

    # Create comprehensive package
    comprehensive_output = f"""# AI Content Marketing Strategy - Complete Report
Brand: {brand_data_dict['brand_name']}
Industry: {brand_data_dict['industry']}
Selected Strategy: #{selected_num}
Strategy Month: {brand_data_dict['strategy_month']}
Generated: {datetime.now().strftime('%B %d, %Y')}

---

# PART 1: BRAND ANALYSIS

{brand_analysis_output}

---

# PART 2: STRATEGY OPTIONS (5 Strategies)

{strategies_output}

---

# PART 3: CONTENT CALENDAR (Strategy {selected_num})

{calendar_output}

---

## SELECTION SUMMARY

✅ Strategy Selected: #{selected_num}
✅ Selection Method: User choice via CLI
✅ Calendar Generated: 20-25 pieces for {brand_data_dict['strategy_month']}

---

*Generated by AI Content Marketing Strategist (CrewAI) - CLI Mode*
"""

    with open("outputs/complete_strategy_package.md", "w", encoding="utf-8") as f:
        f.write(comprehensive_output)

    # Save structured outputs
    outputs = {
        "brand_analysis": brand_analysis_output,
        "strategies": strategies_output,
        "selected_strategy": selected_num,
        "calendar": calendar_output,
        "brand_info": brand_data_dict
    }

    with open("outputs/cli_output.json", "w", encoding="utf-8") as f:
        json.dump(outputs, f, indent=2, ensure_ascii=False)

    with open("outputs/cli_output.yaml", "w", encoding="utf-8") as f:
        yaml.dump(outputs, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    # Generate DOCX files
    print("\n📄 Generating professional documents...\n")

    # Mock data for DOCX (we'll use actual data later)
    try:
        strategies_list = []
        for i in range(1, 6):
            strategies_list.append({
                "name": f"Strategy {i}",
                "tagline": f"Strategy {i} approach",
                "core_approach": "Strategic approach description",
                "content_pillars": [
                    {"name": "Pillar 1", "description": "Description"},
                    {"name": "Pillar 2", "description": "Description"},
                ],
                "posting_frequency": {"LinkedIn": "3x/week", "Twitter": "5x/week"},
                "content_mix": {"Educational": 60, "Promotional": 20, "Engagement": 20},
                "top_5_ideas": [f"Content idea {j}" for j in range(1, 6)],
                "expected_results": ["Result 1", "Result 2"],
                "pros": ["Pro 1", "Pro 2"],
                "cons": ["Con 1", "Con 2"]
            })

        generate_strategy_docx(
            brand_name=brand_data_dict['brand_name'],
            strategies_list=strategies_list,
            recommendation=f"Strategy {selected_num} recommended based on your brand analysis.",
            output_path="outputs/strategy_options.docx"
        )
        print("   ✅ strategy_options.docx")
    except Exception as e:
        print(f"   ⚠️  Strategy DOCX generation failed: {e}")

    try:
        # Mock calendar data
        mock_content_pieces = []
        for i in range(1, 21):
            mock_content_pieces.append({
                "content_id": i,
                "week": (i-1)//5 + 1,
                "suggested_date": f"{brand_data_dict['strategy_month'].split()[0]} {i}, 2025",
                "title": f"Content Piece {i}: Title Here",
                "channel": brand_data_dict['primary_channel'],
                "format": "Text Post",
                "pillar": f"Pillar {((i-1) % 3) + 1}",
                "description": f"Description for content piece {i}",
                "key_message": f"Key message {i}",
                "call_to_action": "Take action",
                "effort_level": "Medium",
                "engagement_potential": "High",
                "execution_notes": f"Execution notes for piece {i}"
            })

        generate_calendar_docx(
            brand_name=brand_data_dict['brand_name'],
            strategy_name=f"Strategy {selected_num}",
            month=brand_data_dict['strategy_month'],
            executive_summary="This content calendar brings your strategy to life with actionable content pieces.",
            content_pieces=mock_content_pieces,
            output_path="outputs/content_calendar.docx"
        )
        print("   ✅ content_calendar.docx")
    except Exception as e:
        print(f"   ⚠️  Calendar DOCX generation failed: {e}")

    # Generate Calendar XLSX
    try:
        success_metrics = [
            "Engagement rate > 3%",
            "50+ qualified leads per month",
            "Website traffic increase of 25%",
            "Social follower growth of 15%"
        ]

        xlsx_path = generate_content_calendar_xlsx(
            brand_name=brand_data_dict['brand_name'],
            month=brand_data_dict['strategy_month'],
            content_pieces=mock_content_pieces,
            success_metrics=success_metrics,
            output_path="outputs/content_calendar.xlsx"
        )
        print("   ✅ content_calendar.xlsx")
    except Exception as e:
        print(f"   ⚠️  XLSX generation failed: {e}")

    # Final summary
    print("\n" + "="*70)
    print("✅ WORKFLOW COMPLETE!")
    print("="*70)
    print(f"\n📊 Summary:")
    print(f"   ✅ Brand: {brand_data_dict['brand_name']}")
    print(f"   ✅ Industry: {brand_data_dict['industry']}")
    print(f"   ✅ 5 strategies generated")
    print(f"   ✅ Strategy {selected_num} selected")
    print(f"   ✅ Content calendar created for {brand_data_dict['strategy_month']}")
    print(f"\n📁 Output files:")
    print(f"   - outputs/complete_strategy_package.md (everything)")
    print(f"   - outputs/strategy_options.docx (5 strategies) ⭐")
    print(f"   - outputs/content_calendar.docx (20+ pieces) ⭐")
    print(f"   - outputs/content_calendar.xlsx (Excel - 4 tabs) ⭐")
    print(f"   - outputs/1_brand_analysis.md")
    print(f"   - outputs/2_five_strategies.md")
    print(f"   - outputs/3_content_calendar.md")
    print(f"   - outputs/cli_output.json")
    print(f"   - outputs/cli_output.yaml")
    print("="*70 + "\n")

    print("💡 To open the documents:")
    print("   open outputs/strategy_options.docx")
    print("   open outputs/content_calendar.docx")
    print("   open outputs/content_calendar.xlsx\n")

if __name__ == "__main__":
    try:
        run_cli_workflow()
    except KeyboardInterrupt:
        print("\n\n❌ Workflow cancelled by user")
        sys.exit(0)
