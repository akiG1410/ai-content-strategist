from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

# Enums for controlled vocabularies
class EffortLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class EngagementPotential(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class ContentFormat(str, Enum):
    TEXT_POST = "Text Post"
    CAROUSEL = "Carousel"
    VIDEO = "Video"
    ARTICLE = "Article"
    POLL = "Poll"
    THREAD = "Thread"
    INFOGRAPHIC = "Infographic"

class Channel(str, Enum):
    LINKEDIN = "LinkedIn"
    TWITTER = "Twitter"
    BLOG = "Blog"
    INSTAGRAM = "Instagram"
    FACEBOOK = "Facebook"

# Brand Analysis Model
class BrandAnalysis(BaseModel):
    brand_positioning: str = Field(description="2-3 sentence summary of brand positioning")
    target_audience: str = Field(description="Description of primary audience")
    key_differentiators: List[str] = Field(description="What sets this brand apart")
    content_opportunities: List[str] = Field(description="Key content angles to pursue")
    constraints: dict = Field(description="Budget, time, and resource constraints")
    strategic_imperatives: List[str] = Field(description="What content must achieve")
    competitive_gaps: List[str] = Field(description="Topics competitors aren't covering")

# Content Pillar Model
class ContentPillar(BaseModel):
    name: str
    description: str
    why_it_matters: str

# Strategy Model
class ContentStrategy(BaseModel):
    strategy_number: int
    name: str
    tagline: str
    core_approach: str
    why_this_strategy: str
    content_pillars: List[ContentPillar]
    posting_frequency: dict = Field(description="Posts per week/month by channel")
    content_mix: dict = Field(description="Percentage breakdown by content type")
    top_5_ideas: List[str]
    estimated_effort_hours: int
    resources_needed: List[str]
    expected_results: List[str]
    pros: List[str]
    cons: List[str]

class StrategyRecommendation(BaseModel):
    recommended_strategy_number: int
    reasoning: str
    week_1_actions: List[str]

class StrategiesOutput(BaseModel):
    strategies: List[ContentStrategy]
    recommendation: StrategyRecommendation

# Content Calendar Model
class ContentPiece(BaseModel):
    content_id: int
    week: int
    suggested_date: str
    title: str
    pillar: str
    channel: Channel
    format: ContentFormat
    key_message: str
    description: str
    call_to_action: str
    effort_level: EffortLevel
    effort_explanation: str
    engagement_potential: EngagementPotential
    engagement_reasoning: str
    seo_keyword: Optional[str] = None
    execution_notes: str

class ContentCalendar(BaseModel):
    executive_summary: str
    content_pieces: List[ContentPiece]
    weekly_breakdown: dict
    content_mix_analysis: dict
    success_metrics: List[str]
    quick_wins: List[int] = Field(description="Content IDs that are quick wins")
    production_notes: str
