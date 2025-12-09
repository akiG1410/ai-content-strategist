"""
Comprehensive input validation with security protections
Prevents XSS, prompt injection, and validates all user inputs
"""

import re
from typing import Dict, List, Tuple, Any, Optional
import html


class InputValidator:
    """Validates and sanitizes all user inputs"""

    # Whitelisted values for dropdown selections
    VALID_INDUSTRIES = [
        "B2B SaaS", "E-commerce - Fashion", "E-commerce - Electronics",
        "Local Services", "Healthcare", "Education", "Finance",
        "Real Estate", "Food & Beverage", "Travel & Hospitality",
        "Marketing Agency", "Consulting", "Manufacturing",
        "Non-Profit", "Entertainment", "Technology Hardware",
        "Professional Services", "Home Services", "Automotive",
        "Beauty & Wellness", "Sports & Fitness", "Media & Publishing",
        "Other"
    ]

    VALID_CHANNELS = [
        "LinkedIn", "Twitter", "Instagram", "Facebook",
        "TikTok", "Blog", "YouTube", "Pinterest",
        "Email Newsletter", "Podcast", "Medium"
    ]

    VALID_TONES = [
        "Professional & Corporate",
        "Professional yet Approachable",
        "Casual & Friendly",
        "Playful & Fun",
        "Authoritative & Expert",
        "Inspirational & Aspirational"
    ]

    VALID_BUDGETS = [
        "Under $500",
        "$500 - $1,000",
        "$1,000 - $2,500",
        "$2,500 - $5,000",
        "$5,000 - $10,000",
        "$10,000+"
    ]

    VALID_TIME_COMMITMENTS = [
        "5-10 hours/week",
        "10-20 hours/week",
        "20-30 hours/week",
        "30+ hours/week"
    ]

    VALID_BUSINESS_GOALS = [
        "Brand Awareness",
        "Lead Generation",
        "Sales",
        "Product Education",
        "Community Building",
        "Customer Retention",
        "Thought Leadership"
    ]

    VALID_RESOURCES = [
        "In-house writer",
        "In-house designer",
        "In-house video editor",
        "Freelancers",
        "AI tools (ChatGPT, etc.)",
        "No dedicated resources"
    ]

    # Dangerous patterns that might indicate injection attempts
    INJECTION_PATTERNS = [
        r'<script',
        r'javascript:',
        r'onerror\s*=',
        r'onclick\s*=',
        r'eval\(',
        r'exec\(',
        r'__import__',
        r'system\(',
        r'os\.system',
        r'subprocess',
        r'\bDROP\b',
        r'\bDELETE\b',
        r'\bUNION\b.*\bSELECT\b',
        r'--\s*$',
        r'/\*.*\*/',
        r'xp_cmdshell',
        r'\bignore\b.*\bprevious\b.*\binstructions\b',
        r'\bignore\b.*\bprior\b',
        r'\bdisregard\b.*\babove\b',
        r'\bforget\b.*\bearlier\b',
        r'\byou\b.*\bare\b.*\bnow\b',
        r'\bact\b.*\bas\b.*\bif\b',
        r'\bpretend\b.*\bto\b.*\bbe\b',
        r'\broleplay\b',
        r'\bsystem\b.*\bprompt\b',
        r'\binject\b',
        r'\boverride\b.*\binstructions\b'
    ]

    def __init__(self):
        """Initialize validator"""
        self.errors: List[str] = []

    def validate_all(self, inputs: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate all inputs at once

        Args:
            inputs: Dictionary of field_name -> value pairs

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        self.errors = []

        # Required fields
        required_fields = ['brand_name', 'industry', 'target_audience', 'business_goals']

        for field in required_fields:
            if field not in inputs or not inputs[field]:
                self.errors.append(f"{field.replace('_', ' ').title()} is required")

        # Validate each field
        if 'brand_name' in inputs:
            self._validate_brand_name(inputs['brand_name'])

        if 'industry' in inputs:
            self._validate_dropdown(inputs['industry'], self.VALID_INDUSTRIES, "Industry")

        if 'website' in inputs and inputs['website']:
            self._validate_url(inputs['website'])

        if 'target_audience' in inputs:
            self._validate_text_area(inputs['target_audience'],
                                     min_length=50,
                                     max_length=2000,
                                     field_name="Target Audience")

        if 'business_goals' in inputs:
            self._validate_multi_select(inputs['business_goals'],
                                        self.VALID_BUSINESS_GOALS,
                                        min_selections=1,
                                        max_selections=4,
                                        field_name="Business Goals")

        if 'active_channels' in inputs:
            self._validate_multi_select(inputs['active_channels'],
                                        self.VALID_CHANNELS,
                                        min_selections=1,
                                        max_selections=11,
                                        field_name="Active Channels")

        if 'primary_channels' in inputs:
            self._validate_multi_select(inputs['primary_channels'],
                                        self.VALID_CHANNELS,
                                        min_selections=1,
                                        max_selections=3,
                                        field_name="Primary Channels")

        if 'brand_tone' in inputs:
            self._validate_dropdown(inputs['brand_tone'], self.VALID_TONES, "Brand Tone")

        if 'monthly_budget' in inputs:
            self._validate_dropdown(inputs['monthly_budget'], self.VALID_BUDGETS, "Monthly Budget")

        if 'time_commitment' in inputs:
            self._validate_dropdown(inputs['time_commitment'],
                                   self.VALID_TIME_COMMITMENTS,
                                   "Time Commitment")

        if 'resources' in inputs:
            self._validate_multi_select(inputs['resources'],
                                        self.VALID_RESOURCES,
                                        min_selections=1,
                                        max_selections=6,
                                        field_name="Resources")

        if 'unique_value_prop' in inputs:
            self._validate_text_area(inputs['unique_value_prop'],
                                     min_length=20,
                                     max_length=1000,
                                     field_name="Unique Value Proposition")

        if 'products_services' in inputs:
            self._validate_text_input(inputs['products_services'],
                                      max_length=500,
                                      field_name="Products/Services")

        if 'competitors' in inputs and inputs['competitors']:
            self._validate_text_input(inputs['competitors'],
                                      max_length=500,
                                      field_name="Competitors")

        if 'past_successes' in inputs and inputs['past_successes']:
            self._validate_text_area(inputs['past_successes'],
                                     min_length=0,
                                     max_length=1000,
                                     field_name="Past Successes")

        if 'additional_notes' in inputs and inputs['additional_notes']:
            self._validate_text_area(inputs['additional_notes'],
                                     min_length=0,
                                     max_length=1000,
                                     field_name="Additional Notes")

        return (len(self.errors) == 0, self.errors)

    def _validate_brand_name(self, value: str) -> bool:
        """Validate brand name"""
        if not value or len(value.strip()) == 0:
            self.errors.append("Brand name cannot be empty")
            return False

        if len(value) > 100:
            self.errors.append("Brand name must be 100 characters or less")
            return False

        if self._contains_injection_pattern(value):
            self.errors.append("Brand name contains invalid characters")
            return False

        # Check for excessive special characters
        special_char_count = sum(1 for c in value if not c.isalnum() and not c.isspace())
        if special_char_count > len(value) * 0.3:
            self.errors.append("Brand name contains too many special characters")
            return False

        return True

    def _validate_text_input(self, value: str, max_length: int, field_name: str) -> bool:
        """Validate single-line text input"""
        if len(value) > max_length:
            self.errors.append(f"{field_name} must be {max_length} characters or less")
            return False

        if self._contains_injection_pattern(value):
            self.errors.append(f"{field_name} contains invalid content")
            return False

        return True

    def _validate_text_area(self, value: str, min_length: int, max_length: int,
                           field_name: str) -> bool:
        """Validate multi-line text input"""
        value_len = len(value.strip())

        if min_length > 0 and value_len < min_length:
            self.errors.append(f"{field_name} must be at least {min_length} characters")
            return False

        if value_len > max_length:
            self.errors.append(f"{field_name} must be {max_length} characters or less")
            return False

        if self._contains_injection_pattern(value):
            self.errors.append(f"{field_name} contains invalid content")
            return False

        return True

    def _validate_url(self, value: str) -> bool:
        """Validate URL format"""
        if not value:
            return True  # URL is optional

        # Basic URL validation
        url_pattern = r'^https?://[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+(:[0-9]+)?(/.*)?$'
        if not re.match(url_pattern, value, re.IGNORECASE):
            self.errors.append("Website URL format is invalid (must start with http:// or https://)")
            return False

        if len(value) > 200:
            self.errors.append("Website URL is too long")
            return False

        return True

    def _validate_dropdown(self, value: str, valid_options: List[str], field_name: str) -> bool:
        """Validate dropdown selection"""
        if value not in valid_options:
            self.errors.append(f"{field_name} selection is invalid")
            return False

        return True

    def _validate_multi_select(self, values: List[str], valid_options: List[str],
                               min_selections: int, max_selections: int,
                               field_name: str) -> bool:
        """Validate multi-select input"""
        if not isinstance(values, list):
            self.errors.append(f"{field_name} must be a list")
            return False

        if len(values) < min_selections:
            self.errors.append(f"{field_name}: Please select at least {min_selections}")
            return False

        if len(values) > max_selections:
            self.errors.append(f"{field_name}: Please select no more than {max_selections}")
            return False

        # Check all values are in whitelist
        for value in values:
            if value not in valid_options:
                self.errors.append(f"{field_name}: Invalid selection '{value}'")
                return False

        return True

    def _contains_injection_pattern(self, value: str) -> bool:
        """Check if value contains potential injection patterns"""
        value_lower = value.lower()

        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True

        return False

    @staticmethod
    def sanitize_text(value: str) -> str:
        """
        Sanitize text for safe display
        Escapes HTML and removes dangerous characters
        """
        if not value:
            return ""

        # HTML escape
        sanitized = html.escape(value)

        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')

        return sanitized

    @staticmethod
    def sanitize_for_filename(value: str) -> str:
        """
        Sanitize string for use in filename
        """
        # Remove/replace dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', value)

        # Limit length
        sanitized = sanitized[:100]

        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(' .')

        if not sanitized:
            sanitized = "document"

        return sanitized
