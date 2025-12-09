# -*- coding: utf-8 -*-
import os
import sys
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
import json

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables
load_dotenv()

# Configure for OpenRouter + Claude
os.environ["OPENAI_API_KEY"] = os.getenv("OPENROUTER_API_KEY")
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
os.environ["OPENAI_MODEL_NAME"] = "anthropic/claude-sonnet-4-20250514"

# Import from main
from main import (
    brand_data,
    brand_analyst,
    strategy_architect,
    content_calendar_specialist,
    generate_strategies
)

from document_generator import generate_strategy_docx, generate_calendar_docx
from excel_generator import generate_content_calendar_xlsx
from competitor_analyzer import CompetitorAnalyzer, parse_competitor_input
import yaml

# For testing, automatically select Strategy 1
SELECTED_STRATEGY = 1

def run_test_workflow():
    """Run complete workflow with automatic strategy selection for testing"""

    print("\n" + "="*70)
    print("🧪 TEST MODE: Running workflow with auto-select Strategy 1")
    print("="*70 + "\n")

    # Add competitor information to the brand data
    competitor_string = "Asana, Monday.com, ClickUp"

    # Parse and analyze competitors
    print("\n" + "="*70)
    print("🔬 COMPETITOR ANALYSIS")
    print("="*70 + "\n")

    competitors_parsed = parse_competitor_input(competitor_string)

    if competitors_parsed:
        try:
            analyzer = CompetitorAnalyzer()
            competitor_analysis = analyzer.analyze_competitors(competitors_parsed)
            competitor_analysis_text = analyzer.format_for_agent(competitor_analysis)

            # Save competitor analysis
            with open("outputs/0_competitor_analysis.md", "w", encoding="utf-8") as f:
                f.write(competitor_analysis_text)

            print("✅ Competitor analysis saved to outputs/0_competitor_analysis.md\n")
        except Exception as e:
            print(f"⚠️  Competitor analysis failed: {str(e)}")
            print("   Continuing without competitor insights...\n")
            competitor_analysis_text = "No competitor analysis available."
    else:
        print("ℹ️  No competitors specified, skipping analysis\n")
        competitor_analysis_text = "No competitor analysis available."

    # Create analyze_brand task with competitor context
    analyze_brand = Task(
        description=f"""
        Analyze the following brand information and competitor landscape:

        BRAND INFORMATION:
        {brand_data}

        COMPETITOR ANALYSIS:
        {competitor_analysis_text}

        Your analysis should include:
        1. Brand positioning summary (2-3 sentences)
        2. Primary audience characteristics and pain points
        3. Key differentiators from competitors (USE THE COMPETITOR DATA)
        4. Content opportunities based on goals and COMPETITOR GAPS
        5. Channel-specific considerations
        6. Constraints (budget, time, resources)
        7. Strategic imperatives (what MUST the content achieve?)
        8. Competitive positioning recommendations (based on competitor analysis)
        """,
        expected_output="A structured brand analysis document",
        agent=brand_analyst
    )

    # PHASE 1: Brand Analysis + Strategy Generation
    print("📋 PHASE 1: Analyzing brand and generating 5 strategy options...")

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

    print(f"\n✅ Phase 1 Complete! Auto-selecting Strategy {SELECTED_STRATEGY}...\n")

    # PHASE 2: Content Calendar
    print("📅 PHASE 2: Creating detailed content calendar...")

    build_calendar_test = Task(
        description=f"""
        Create a detailed content calendar for January 2025 based on Strategy {SELECTED_STRATEGY}.

        Generate exactly 20-25 content pieces with all required fields.
        """,
        expected_output="Complete content calendar with 20-25 pieces",
        agent=content_calendar_specialist,
        context=[analyze_brand, generate_strategies]
    )

    phase2_crew = Crew(
        agents=[content_calendar_specialist],
        tasks=[build_calendar_test],
        process=Process.sequential,
        verbose=True
    )

    calendar_result = phase2_crew.kickoff()
    calendar_output = str(calendar_result)

    # Save all markdown outputs
    with open("outputs/1_brand_analysis.md", "w", encoding="utf-8") as f:
        f.write(brand_analysis_output)

    with open("outputs/2_five_strategies.md", "w", encoding="utf-8") as f:
        f.write(strategies_output)

    with open("outputs/3_content_calendar.md", "w", encoding="utf-8") as f:
        f.write(calendar_output)

    comprehensive_output = f"""# AI Content Marketing Strategy - Complete Report
Generated: January 2025
Brand: CloudFlow
Selected Strategy: #{SELECTED_STRATEGY}

---

# PART 1: BRAND ANALYSIS

{brand_analysis_output}

---

# PART 2: STRATEGY OPTIONS

{strategies_output}

---

# PART 3: CONTENT CALENDAR (Strategy {SELECTED_STRATEGY})

{calendar_output}
"""

    with open("outputs/complete_strategy_package.md", "w", encoding="utf-8") as f:
        f.write(comprehensive_output)

    # Save structured outputs (string version for test)
    outputs = {
        "brand_analysis": brand_analysis_output,
        "strategies": strategies_output,
        "calendar": calendar_output
    }

    with open("outputs/structured_output.json", "w", encoding="utf-8") as f:
        json.dump(outputs, f, indent=2, ensure_ascii=False)

    with open("outputs/structured_output.yaml", "w", encoding="utf-8") as f:
        yaml.dump(outputs, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print("\n📄 Generating professional DOCX documents...")

    # Generate Strategy Options DOCX
    try:
        # Mock structured data for DOCX
        strategies_structured = []
        for i in range(1, 6):
            strategies_structured.append({
                "name": f"Strategy {i}",
                "tagline": f"Strategic approach {i}",
                "core_approach": "Core approach description for this strategy.",
                "content_pillars": [
                    {"name": "Pillar 1", "description": "First content pillar"},
                    {"name": "Pillar 2", "description": "Second content pillar"},
                    {"name": "Pillar 3", "description": "Third content pillar"},
                ],
                "posting_frequency": {
                    "LinkedIn": "3-4x per week",
                    "Twitter": "Daily",
                    "Blog": "2x per month"
                },
                "content_mix": {
                    "Educational": 60,
                    "Promotional": 20,
                    "Engagement": 15,
                    "Curated": 5
                },
                "top_5_ideas": [
                    f"Content idea 1 for strategy {i}",
                    f"Content idea 2 for strategy {i}",
                    f"Content idea 3 for strategy {i}",
                    f"Content idea 4 for strategy {i}",
                    f"Content idea 5 for strategy {i}",
                ],
                "expected_results": [
                    "Expected result 1",
                    "Expected result 2",
                    "Expected result 3"
                ],
                "pros": [
                    "Advantage 1",
                    "Advantage 2",
                    "Advantage 3"
                ],
                "cons": [
                    "Challenge 1",
                    "Challenge 2"
                ]
            })

        strategy_docx_path = generate_strategy_docx(
            brand_name="CloudFlow",
            strategies_list=strategies_structured,
            recommendation=f"Based on the analysis, Strategy {SELECTED_STRATEGY} is recommended for CloudFlow.",
            output_path="outputs/strategy_options.docx"
        )
        print(f"   ✅ Strategy options: {strategy_docx_path}")
    except Exception as e:
        print(f"   ⚠️  Strategy DOCX failed: {str(e)}")
        import traceback
        traceback.print_exc()

    # Generate Calendar DOCX
    try:
        mock_content_pieces = []
        for i in range(1, 21):
            mock_content_pieces.append({
                "content_id": i,
                "week": (i-1)//5 + 1,
                "suggested_date": f"January {i}, 2025 (Monday)",
                "title": f"Content Piece {i}: Engaging Title Here",
                "channel": "LinkedIn" if i % 2 == 0 else "Twitter",
                "format": "Carousel" if i % 3 == 0 else "Text Post",
                "pillar": f"Pillar {((i-1) % 3) + 1}",
                "description": f"This is a detailed description for content piece {i}. It explains what the content is about and why it matters.",
                "key_message": f"Key message for piece {i}",
                "call_to_action": "Visit our website" if i % 4 == 0 else "Download the guide",
                "effort_level": "Medium",
                "engagement_potential": "High",
                "execution_notes": f"Tips for creating content piece {i}"
            })

        calendar_docx_path = generate_calendar_docx(
            brand_name="CloudFlow",
            strategy_name=f"Strategy {SELECTED_STRATEGY}",
            month="January 2025",
            executive_summary="This content calendar brings your chosen strategy to life with 20 actionable content pieces designed to achieve your business goals.",
            content_pieces=mock_content_pieces,
            output_path="outputs/content_calendar.docx"
        )
        print(f"   ✅ Content calendar: {calendar_docx_path}")
    except Exception as e:
        print(f"   ⚠️  Calendar DOCX failed: {str(e)}")
        import traceback
        traceback.print_exc()

    # Generate Calendar XLSX
    try:
        success_metrics = [
            "Engagement rate > 3%",
            "50+ qualified leads",
            "Website traffic +25%",
            "Follower growth +15%"
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
        import traceback
        traceback.print_exc()

    # Final summary
    print("\n" + "="*70)
    print("✅ TEST WORKFLOW COMPLETE!")
    print("="*70)
    print(f"\n📊 Summary:")
    print(f"   ✅ Brand analyzed")
    print(f"   ✅ 5 strategies generated")
    print(f"   ✅ Strategy {SELECTED_STRATEGY} auto-selected")
    print(f"   ✅ Content calendar created")
    print(f"   ✅ DOCX & XLSX documents generated")
    print(f"\n📁 Output files:")
    print(f"   - outputs/0_competitor_analysis.md ⭐ (competitor insights)")
    print(f"   - outputs/strategy_options.docx ⭐ (5 strategies)")
    print(f"   - outputs/content_calendar.docx ⭐ (20 pieces)")
    print(f"   - outputs/content_calendar.xlsx ⭐ (Excel - 4 tabs)")
    print(f"   - outputs/complete_strategy_package.md")
    print(f"   - outputs/structured_output.json")
    print(f"   - outputs/structured_output.yaml")
    print("="*70 + "\n")

    print("💡 To open the documents on Mac:")
    print("   open outputs/strategy_options.docx")
    print("   open outputs/content_calendar.docx")
    print("   open outputs/content_calendar.xlsx")

if __name__ == "__main__":
    run_test_workflow()
