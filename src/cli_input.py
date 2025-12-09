# -*- coding: utf-8 -*-
import sys
from datetime import datetime

class BrandInputCollector:
    """Interactive CLI for collecting brand information"""

    def __init__(self):
        self.data = {}

    def print_header(self):
        """Print welcome header"""
        print("\n" + "="*70)
        print("🎯 AI CONTENT MARKETING STRATEGIST")
        print("="*70)
        print("\nWelcome! I'll ask you some questions about your brand to create")
        print("a personalized content marketing strategy.\n")
        print("This will take about 5 minutes to complete.")
        print("="*70 + "\n")

    def get_input(self, prompt, required=True, default=None):
        """Get input from user with validation"""
        while True:
            if default:
                user_input = input(f"{prompt} [{default}]: ").strip()
                if not user_input:
                    return default
            else:
                user_input = input(f"{prompt}: ").strip()

            if user_input or not required:
                return user_input

            if required:
                print("❌ This field is required. Please provide a value.\n")

    def get_multiline_input(self, prompt, required=True):
        """Get multiline input from user"""
        print(f"\n{prompt}")
        print("(Press Enter twice when done, or Ctrl+D)\n")
        lines = []
        try:
            while True:
                line = input()
                if line == "" and lines:  # Empty line after content
                    break
                lines.append(line)
        except EOFError:
            pass

        result = "\n".join(lines).strip()

        if required and not result:
            print("❌ This field is required.\n")
            return self.get_multiline_input(prompt, required)

        return result

    def get_choice(self, prompt, options, allow_multiple=False):
        """Get choice from predefined options"""
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")

        if allow_multiple:
            print("\nEnter numbers separated by commas (e.g., 1,3,5)")
            choices = input("Your selection: ").strip()
            try:
                indices = [int(x.strip()) - 1 for x in choices.split(",")]
                selected = [options[i] for i in indices if 0 <= i < len(options)]
                if selected:
                    return selected
            except:
                pass
            print("❌ Invalid selection. Please try again.")
            return self.get_choice(prompt, options, allow_multiple)
        else:
            choice = input("Your selection (number): ").strip()
            try:
                index = int(choice) - 1
                if 0 <= index < len(options):
                    return options[index]
            except:
                pass
            print("❌ Invalid selection. Please try again.")
            return self.get_choice(prompt, options, allow_multiple)

    def collect_all(self):
        """Collect all brand information"""
        self.print_header()

        # Section 1: Brand Basics
        print("📋 SECTION 1: BRAND BASICS\n")

        self.data['brand_name'] = self.get_input("Brand Name", required=True)

        industries = [
            "B2B SaaS", "E-commerce - Fashion", "E-commerce - Electronics",
            "Local Services", "Healthcare", "Education", "Finance",
            "Real Estate", "Food & Beverage", "Travel & Hospitality",
            "Marketing Agency", "Consulting", "Manufacturing",
            "Non-Profit", "Entertainment", "Technology Hardware",
            "Professional Services", "Home Services", "Automotive",
            "Beauty & Wellness", "Sports & Fitness", "Media & Publishing",
            "Other"
        ]
        self.data['industry'] = self.get_choice("Select your industry:", industries)

        self.data['website'] = self.get_input("Company Website (optional)", required=False, default="")

        # Section 2: Target Audience
        print("\n" + "="*70)
        print("👥 SECTION 2: TARGET AUDIENCE\n")

        self.data['target_audience'] = self.get_multiline_input(
            "Describe your target audience in detail:\n"
            "- Who are they?\n"
            "- What are their pain points?\n"
            "- What motivates them?",
            required=True
        )

        # Section 3: Business Goals
        print("\n" + "="*70)
        print("🎯 SECTION 3: BUSINESS GOALS\n")

        goals = [
            "Brand Awareness",
            "Lead Generation",
            "Sales",
            "Product Education",
            "Community Building",
            "Customer Retention",
            "Thought Leadership"
        ]
        self.data['business_goals'] = self.get_choice(
            "Select your primary business goals (up to 4):",
            goals,
            allow_multiple=True
        )

        # Section 4: Content Channels
        print("\n" + "="*70)
        print("📱 SECTION 4: CONTENT CHANNELS\n")

        channels = [
            "LinkedIn", "Twitter", "Instagram", "Facebook",
            "TikTok", "Blog", "YouTube", "Pinterest",
            "Email Newsletter", "Podcast", "Medium"
        ]
        self.data['active_channels'] = self.get_choice(
            "Which channels do you want to focus on?",
            channels,
            allow_multiple=True
        )

        self.data['primary_channel'] = self.get_choice(
            "Which is your PRIMARY channel?",
            self.data['active_channels']
        )

        # Section 5: Resources & Constraints
        print("\n" + "="*70)
        print("⚙️  SECTION 5: RESOURCES & CONSTRAINTS\n")

        tones = [
            "Professional & Corporate",
            "Professional yet Approachable",
            "Casual & Friendly",
            "Playful & Fun",
            "Authoritative & Expert",
            "Inspirational & Aspirational"
        ]
        self.data['brand_tone'] = self.get_choice("Select your brand tone:", tones)

        budgets = [
            "Under $500",
            "$500 - $1,000",
            "$1,000 - $2,500",
            "$2,500 - $5,000",
            "$5,000 - $10,000",
            "$10,000+"
        ]
        self.data['monthly_budget'] = self.get_choice("Monthly content budget:", budgets)

        time_commitments = [
            "5-10 hours/week",
            "10-20 hours/week",
            "20-30 hours/week",
            "30+ hours/week"
        ]
        self.data['time_commitment'] = self.get_choice("Weekly time commitment:", time_commitments)

        resources = [
            "In-house writer",
            "In-house designer",
            "In-house video editor",
            "Freelancers",
            "AI tools (ChatGPT, etc.)",
            "No dedicated resources"
        ]
        self.data['resources'] = self.get_choice(
            "What content creation resources do you have?",
            resources,
            allow_multiple=True
        )

        # Section 6: Brand Details
        print("\n" + "="*70)
        print("💡 SECTION 6: BRAND DETAILS\n")

        self.data['unique_value_prop'] = self.get_multiline_input(
            "What's your Unique Value Proposition?\n"
            "(What makes you different from competitors?)",
            required=True
        )

        self.data['products_services'] = self.get_input(
            "List your key products/services (comma-separated)",
            required=True
        )

        # Section 7: Additional Context
        print("\n" + "="*70)
        print("📝 SECTION 7: ADDITIONAL CONTEXT\n")

        self.data['competitors'] = self.get_input(
            "List main competitors (optional, comma-separated)",
            required=False,
            default=""
        )

        self.data['past_successes'] = self.get_input(
            "Any past content that worked well? (optional)",
            required=False,
            default=""
        )

        months = [
            "January 2025", "February 2025", "March 2025",
            "April 2025", "May 2025", "June 2025"
        ]
        self.data['strategy_month'] = self.get_choice(
            "Which month should we plan for?",
            months
        )

        self.data['additional_notes'] = self.get_input(
            "Any additional notes? (optional)",
            required=False,
            default=""
        )

        return self.data

    def display_summary(self):
        """Display collected information for confirmation"""
        print("\n" + "="*70)
        print("📊 SUMMARY OF YOUR INPUT")
        print("="*70 + "\n")

        print(f"Brand: {self.data['brand_name']}")
        print(f"Industry: {self.data['industry']}")
        print(f"Primary Channel: {self.data['primary_channel']}")
        print(f"Business Goals: {', '.join(self.data['business_goals'])}")
        print(f"Strategy Month: {self.data['strategy_month']}")
        print("\n" + "="*70 + "\n")

    def confirm(self):
        """Ask user to confirm the input"""
        while True:
            response = input("Is this information correct? (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                return True
            elif response in ['no', 'n']:
                return False
            print("Please enter 'yes' or 'no'")

    def format_for_workflow(self):
        """Format collected data for the workflow"""
        return f"""
Brand Name: {self.data['brand_name']}
Industry: {self.data['industry']}
Company Website: {self.data.get('website', 'Not provided')}
Target Audience: {self.data['target_audience']}
Business Goals: {', '.join(self.data['business_goals'])}
Active Channels: {', '.join(self.data['active_channels'])}
Primary Channel: {self.data['primary_channel']}
Brand Tone: {self.data['brand_tone']}
Monthly Budget: {self.data['monthly_budget']}
Weekly Time Commitment: {self.data['time_commitment']}
Content Creation Resources: {', '.join(self.data['resources'])}
Unique Value Proposition: {self.data['unique_value_prop']}
Key Products/Services: {self.data['products_services']}
Competitors: {self.data.get('competitors', 'Not provided')}
Past Successful Content: {self.data.get('past_successes', 'Not provided')}
Strategy Month: {self.data['strategy_month']}
Additional Notes: {self.data.get('additional_notes', 'None')}
"""


def collect_brand_input():
    """Main function to collect brand input via CLI"""
    collector = BrandInputCollector()

    while True:
        data = collector.collect_all()
        collector.display_summary()

        if collector.confirm():
            print("\n✅ Great! Starting strategy generation...\n")
            return collector.format_for_workflow(), data
        else:
            print("\n🔄 Let's start over...\n")
