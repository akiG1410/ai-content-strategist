# Interactive Mode - User Guide

## Overview

The Interactive Mode allows you to review all 5 generated content strategies and **choose which one** to expand into a full content calendar. This gives you more control over the final output.

## How to Run

```bash
cd content-strategy-crew
python src/interactive_workflow.py
```

## Workflow Steps

### Phase 1: Strategy Generation (90-120 seconds)

The system will:
1. Analyze the CloudFlow brand
2. Generate 5 complete content strategies
3. Display all strategies for your review

### Interactive Selection

You'll see a summary like this:

```
📊 STRATEGY OPTIONS SUMMARY
======================================================================

**Strategy 1: AI Innovation Thought Leadership**
Tagline: "Where AI Meets Marketing Excellence"
...

**Strategy 2: Community-Driven Success Stories**
Tagline: "Real Teams, Real Results"
...

[Strategies 3-5 displayed...]

======================================================================

👉 Which strategy would you like to expand into a full content calendar? (1-5):
```

**Enter a number from 1-5** to select your preferred strategy.

### Phase 2: Calendar Generation (60-90 seconds)

The system will:
1. Create 20-25 detailed content pieces for January 2025
2. Base all content on your selected strategy
3. Include weekly breakdowns, content mix analysis, and quick wins

## Output Files

After completion, you'll have:

**Comprehensive Reports:**
- `outputs/complete_strategy_package_interactive.md` - Full report with your selection
- `outputs/interactive_output.json` - Structured data (JSON)
- `outputs/interactive_output.yaml` - Structured data (YAML)

**Individual Components:**
- `outputs/1_brand_analysis.md` - Brand analysis
- `outputs/2_five_strategies.md` - All 5 strategies
- `outputs/3_content_calendar.md` - Calendar for selected strategy

## Example Session

```bash
$ python src/interactive_workflow.py

======================================================================
🚀 AI CONTENT MARKETING STRATEGIST - INTERACTIVE MODE
======================================================================

📋 PHASE 1: Analyzing brand and generating 5 strategy options...
   This will take about 90-120 seconds...

[AI generates strategies...]

✅ Phase 1 Complete!
   - Brand analysis saved to outputs/1_brand_analysis.md
   - 5 strategies saved to outputs/2_five_strategies.md

======================================================================
📊 STRATEGY OPTIONS SUMMARY
======================================================================

[5 strategies displayed]

👉 Which strategy would you like to expand into a full content calendar? (1-5): 3

✅ You selected Strategy 3
   Generating detailed content calendar...

📅 PHASE 2: Creating detailed content calendar...
   This will take about 60-90 seconds...

[AI generates calendar...]

======================================================================
✅ WORKFLOW COMPLETE!
======================================================================

📊 Summary:
   ✅ Brand analyzed
   ✅ 5 strategies generated
   ✅ Strategy 3 selected (your choice)
   ✅ Content calendar created (20+ pieces)

📁 Output files:
   - outputs/complete_strategy_package_interactive.md (everything)
   - outputs/1_brand_analysis.md
   - outputs/2_five_strategies.md
   - outputs/3_content_calendar.md
   - outputs/interactive_output.json
   - outputs/interactive_output.yaml
======================================================================
```

## Comparison: Automatic vs Interactive Mode

| Feature | Automatic Mode | Interactive Mode |
|---------|----------------|------------------|
| **Run Command** | `python src/main.py` | `python src/interactive_workflow.py` |
| **Strategy Selection** | Pre-configured (Strategy 1) | User chooses (1-5) |
| **User Interaction** | None | Manual selection required |
| **Execution Time** | ~3 minutes | ~3-4 minutes |
| **Best For** | Automation, CI/CD | Manual review, testing |

## Tips

1. **Review Carefully**: Take time to read all 5 strategies before selecting
2. **Consider Goals**: Match the strategy to your specific business objectives
3. **Check Resources**: Ensure you have the team capacity for the selected strategy
4. **Save Outputs**: All files are saved, so you can compare strategies later

## Customization

To modify the brand being analyzed, edit the `brand_data` variable in `src/interactive_workflow.py`:

```python
brand_data = """
Brand Name: YourBrand
Industry: Your Industry
...
"""
```

## Troubleshooting

**Issue: "Please enter a valid number"**
- Solution: Enter only digits 1-5, no spaces or letters

**Issue: Workflow takes too long**
- Normal: First run may take 3-4 minutes
- Check: Verify your OpenRouter API key has credits

**Issue: Ctrl+C to cancel**
- The workflow handles keyboard interrupts gracefully
- Files from Phase 1 will still be saved if you cancel during Phase 2
