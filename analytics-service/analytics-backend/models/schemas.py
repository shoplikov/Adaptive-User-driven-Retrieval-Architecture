"""Pydantic models for analytics API responses."""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

from typing import TypeVar, Generic

# Define a type variable for the data field
DataType = TypeVar('DataType')

class AnalyticsResponse(BaseModel, Generic[DataType]):
    """Standard response format for analytics API."""
    status: str = Field(..., description="Response status")
    data: DataType = Field(..., description="Response data")
    timestamp: str = Field(..., description="Timestamp of response")
    cache_ttl: Optional[int] = Field(None, description="Cache TTL in seconds")

class MetricsOverview(BaseModel):
    """Overview of all key metrics."""
    total_conversations: int = Field(..., description="Total number of conversations")
    active_conversations: int = Field(..., description="Number of active conversations")
    positive_satisfaction: float = Field(..., description="Percentage of positive satisfaction scores")
    average_tokens: float = Field(..., description="Average tokens per conversation")
    status_breakdown: Dict[str, int] = Field(..., description="Conversation status breakdown")

class SatisfactionMetrics(BaseModel):
    """Satisfaction score metrics."""
    total_turns: int = Field(..., description="Total number of conversation turns")
    positive_count: int = Field(..., description="Number of positive satisfaction scores")
    neutral_count: int = Field(..., description="Number of neutral satisfaction scores")
    negative_count: int = Field(..., description="Number of negative satisfaction scores")
    positive_percentage: float = Field(..., description="Percentage of positive satisfaction scores")
    neutral_percentage: float = Field(..., description="Percentage of neutral satisfaction scores")
    negative_percentage: float = Field(..., description="Percentage of negative satisfaction scores")

class TokenUsage(BaseModel):
    """Token usage statistics."""
    total_tokens: int = Field(..., description="Total tokens used")
    average_tokens: float = Field(..., description="Average tokens per conversation")
    max_tokens: int = Field(..., description="Maximum tokens in a single conversation")
    min_tokens: int = Field(..., description="Minimum tokens in a single conversation")

class StatusBreakdown(BaseModel):
    """Conversation status breakdown."""
    active: int = Field(..., description="Number of active conversations")
    inactive: int = Field(..., description="Number of inactive conversations")
    ended: int = Field(..., description="Number of ended conversations")
    other: int = Field(..., description="Number of conversations with other statuses")

class TrendData(BaseModel):
    """Time-based trend data."""
    period: str = Field(..., description="Time period (daily, weekly, monthly)")
    data: List[Dict[str, Any]] = Field(..., description="Trend data points")