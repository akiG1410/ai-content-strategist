import re
import json
from typing import List, Dict, Optional

class ContentCalendarParser:
    """Parse AI-generated content calendar text into structured data"""

    def parse_calendar_output(self, calendar_text: str) -> Dict:
        """
        Parse the full calendar output from Content Calendar Specialist

        Returns:
            Dict with executive_summary, content_pieces, pillars, etc.
        """
        result = {
            "executive_summary": "",
            "content_pieces": [],
            "pillars": {},
            "weekly_breakdown": {},
            "success_metrics": [],
            "quick_wins": []
        }

        # Extract executive summary
        exec_match = re.search(r'(?:EXECUTIVE SUMMARY|Executive Summary)[:\n]+(.*?)(?=\n#{1,3}|\n\*\*|$)',
                              calendar_text, re.DOTALL | re.IGNORECASE)
        if exec_match:
            result['executive_summary'] = exec_match.group(1).strip()

        # Extract content pillars with descriptions
        result['pillars'] = self._extract_pillars(calendar_text)

        # Extract content pieces
        result['content_pieces'] = self._extract_content_pieces(calendar_text)

        # Extract success metrics
        metrics_match = re.search(r'(?:SUCCESS METRICS|Success Metrics)[:\n]+(.*?)(?=\n#{1,3}|\n\*\*|$)',
                                 calendar_text, re.DOTALL | re.IGNORECASE)
        if metrics_match:
            metrics_text = metrics_match.group(1)
            result['success_metrics'] = [m.strip('- •\n') for m in metrics_text.split('\n') if m.strip()]

        # Extract quick wins
        qw_match = re.search(r'(?:QUICK WINS|Quick Wins)[:\n]+(.*?)(?=\n#{1,3}|\n\*\*|$)',
                            calendar_text, re.DOTALL | re.IGNORECASE)
        if qw_match:
            qw_text = qw_match.group(1)
            result['quick_wins'] = [q.strip('- •\n') for q in qw_text.split('\n') if q.strip()]

        return result

    def _extract_pillars(self, text: str) -> Dict[str, str]:
        """Extract content pillars with their descriptions"""
        pillars = {}

        # Look for pillar definitions
        pillar_section = re.search(r'(?:CONTENT PILLARS|Content Pillars)[:\n]+(.*?)(?=\n#{1,3}[^#]|\n\*\*[A-Z]|$)',
                                  text, re.DOTALL | re.IGNORECASE)

        if pillar_section:
            pillar_text = pillar_section.group(1)

            # Match patterns like "Pillar 1: Name - Description" or "**Pillar 1:**"
            pillar_matches = re.finditer(r'(?:Pillar\s+(\d+)[:\s]+)([^\n]+?)(?:\n|$)', pillar_text, re.IGNORECASE)

            for match in pillar_matches:
                pillar_num = f"Pillar {match.group(1)}"
                pillar_desc = match.group(2).strip(' -:')
                pillars[pillar_num] = pillar_desc

        # Fallback: generic pillars
        if not pillars:
            pillars = {
                "Pillar 1": "Brand Awareness & Thought Leadership",
                "Pillar 2": "Product Education & Features",
                "Pillar 3": "Community Engagement & Stories"
            }

        return pillars

    def _extract_content_pieces(self, text: str) -> List[Dict]:
        """Extract individual content pieces from calendar text"""
        pieces = []

        # Try to find structured content blocks first
        # Pattern 1: "Content #1:" or "Content Piece #1:" format
        pattern1 = r'(?:Content\s*(?:Piece)?\s*#?\s*(\d+))[:\s]*([^\n]+?)(?:\n|$)(.*?)(?=(?:Content\s*(?:Piece)?\s*#?\s*\d+)|$)'

        matches = list(re.finditer(pattern1, text, re.DOTALL | re.IGNORECASE))

        if matches:
            # Successfully found structured content
            for match in matches:
                try:
                    content_id = int(match.group(1))
                    title = match.group(2).strip(' :-*"')
                    details = match.group(3)

                    piece = self._parse_content_details(content_id, title, details)
                    if piece:
                        pieces.append(piece)
                except (ValueError, AttributeError) as e:
                    # Skip malformed entries
                    continue
        else:
            # Fallback: try to extract from any numbered list
            # Pattern 2: Simple numbered list "1. Title" or "1) Title"
            pattern2 = r'(?:^|\n)\s*(\d+)[\.\)]\s*([^\n]+)'

            list_matches = list(re.finditer(pattern2, text, re.MULTILINE))

            for match in list_matches:
                try:
                    content_id = int(match.group(1))
                    title = match.group(2).strip()

                    # Create basic piece structure
                    piece = {
                        "content_id": content_id,
                        "title": title,
                        "week": (content_id - 1) // 5 + 1,
                        "suggested_date": "",
                        "channel": "",
                        "format": "",
                        "pillar": "",
                        "key_message": "",
                        "description": "",
                        "call_to_action": "",
                        "effort_level": "Medium",
                        "effort_explanation": "",
                        "engagement_potential": "Medium",
                        "engagement_reasoning": "",
                        "seo_keyword": "",
                        "execution_notes": ""
                    }
                    pieces.append(piece)
                except (ValueError, AttributeError):
                    continue

        return pieces

    def _parse_content_details(self, content_id: int, title: str, details_text: str) -> Dict:
        """Parse details for a single content piece"""
        piece = {
            "content_id": content_id,
            "title": title,
            "week": (content_id - 1) // 5 + 1,
            "suggested_date": "",
            "channel": "",
            "format": "",
            "pillar": "",
            "key_message": "",
            "description": "",
            "call_to_action": "",
            "effort_level": "Medium",
            "effort_explanation": "",
            "engagement_potential": "Medium",
            "engagement_reasoning": "",
            "seo_keyword": "",
            "execution_notes": ""
        }

        # Extract each field using regex with try/except
        fields_to_extract = {
            'week': r'Week[:\s]+(\d+)',
            'suggested_date': r'(?:Date|Suggested Date)[:\s]+([^\n]+)',
            'channel': r'Channel[:\s]+([^\n]+)',
            'format': r'Format[:\s]+([^\n]+)',
            'pillar': r'Pillar[:\s]+([^\n]+)',
            'key_message': r'Key Message[:\s]+([^\n]+)',
            'description': r'Description[:\s]+([^\n]+(?:\n(?![\w\s]*:)[^\n]+)*)',
            'call_to_action': r'(?:Call to Action|CTA)[:\s]+([^\n]+)',
            'effort_level': r'Effort(?:\s+Level)?[:\s]+([^\n]+)',
            'effort_explanation': r'Effort Explanation[:\s]+([^\n]+)',
            'engagement_potential': r'Engagement(?:\s+Potential)?[:\s]+([^\n]+)',
            'engagement_reasoning': r'Engagement Reasoning[:\s]+([^\n]+)',
            'seo_keyword': r'SEO Keyword[:\s]+([^\n]+)',
            'execution_notes': r'Execution Notes[:\s]+([^\n]+(?:\n(?![\w\s]*:)[^\n]+)*)'
        }

        for field, pattern in fields_to_extract.items():
            try:
                match = re.search(pattern, details_text, re.IGNORECASE)
                if match:
                    value = match.group(1).strip(' -•\n"\'')
                    if value:  # Only update if non-empty
                        piece[field] = value
            except (IndexError, AttributeError):
                # Keep default value if extraction fails
                continue

        return piece


def parse_strategies_output(strategies_text: str) -> List[Dict]:
    """
    Parse the 5 strategies from Strategy Architect output

    Returns:
        List of 5 strategy dictionaries
    """
    strategies = []

    # Match strategy blocks (Strategy 1:, Strategy 2:, etc.)
    pattern = r'(?:Strategy\s+#?\s*(\d+)[:\s]*[^\n]*\n)(.*?)(?=(?:Strategy\s+#?\s*\d+)|(?:RECOMMENDATION|## RECOMMENDATION)|$)'

    matches = re.finditer(pattern, strategies_text, re.DOTALL | re.IGNORECASE)

    for match in matches:
        strategy_num = int(match.group(1))
        strategy_text = match.group(2)

        strategy = {
            "strategy_number": strategy_num,
            "name": "",
            "tagline": "",
            "core_approach": "",
            "content_pillars": [],
            "posting_frequency": {},
            "content_mix": {},
            "top_5_ideas": [],
            "pros": [],
            "cons": []
        }

        # Extract name/tagline
        name_match = re.search(r'(?:Name|Strategy Name)[:\s]+([^\n]+)', strategy_text, re.IGNORECASE)
        if name_match:
            strategy['name'] = name_match.group(1).strip(' "*')

        tagline_match = re.search(r'Tagline[:\s]+([^\n]+)', strategy_text, re.IGNORECASE)
        if tagline_match:
            strategy['tagline'] = tagline_match.group(1).strip(' "*')

        # Extract core approach
        approach_match = re.search(r'(?:Core Approach|Approach)[:\s]+([^\n]+(?:\n(?![\w\s]*:)[^\n]+)*)',
                                  strategy_text, re.IGNORECASE)
        if approach_match:
            strategy['core_approach'] = approach_match.group(1).strip()

        # Extract content pillars
        pillars_match = re.search(r'Content Pillars[:\s]+(.*?)(?=\n\*\*[A-Z]|\nPosting|$)',
                                 strategy_text, re.DOTALL | re.IGNORECASE)
        if pillars_match:
            pillars_text = pillars_match.group(1)
            pillar_items = re.findall(r'[-•]\s*([^:\n]+):\s*([^\n]+)', pillars_text)
            for name, desc in pillar_items:
                strategy['content_pillars'].append({
                    "name": name.strip(),
                    "description": desc.strip()
                })

        # Extract top 5 ideas
        ideas_match = re.search(r'(?:Top 5 Content Ideas|Content Ideas)[:\s]+(.*?)(?=\n\*\*[A-Z]|\nEstimated|$)',
                               strategy_text, re.DOTALL | re.IGNORECASE)
        if ideas_match:
            ideas_text = ideas_match.group(1)
            ideas = re.findall(r'(?:\d+\.|[-•])\s*([^\n]+)', ideas_text)
            strategy['top_5_ideas'] = [idea.strip(' "') for idea in ideas if idea.strip()]

        # Extract pros
        pros_match = re.search(r'Pros[:\s]+(.*?)(?=\nCons|\n\*\*[A-Z]|$)',
                              strategy_text, re.DOTALL | re.IGNORECASE)
        if pros_match:
            pros_text = pros_match.group(1)
            strategy['pros'] = [p.strip(' -•\n') for p in pros_text.split('\n') if p.strip() and not p.strip().startswith('*')]

        # Extract cons
        cons_match = re.search(r'Cons[:\s]+(.*?)(?=\n\*\*[A-Z]|$)',
                              strategy_text, re.DOTALL | re.IGNORECASE)
        if cons_match:
            cons_text = cons_match.group(1)
            strategy['cons'] = [c.strip(' -•\n') for c in cons_text.split('\n') if c.strip() and not c.strip().startswith('*')]

        strategies.append(strategy)

    return strategies
