"""
Pydantic models for OpenAI-compatible request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Message(BaseModel):
    """
    Message model representing a single message in a conversation.
    """

    role: str = Field(
        ..., description="The role of the message sender (system, user, assistant)"
    )
    content: str = Field(..., description="The content of the message")


class ChatCompletionRequest(BaseModel):
    """
    OpenAI-compatible chat completion request model.
    """

    model: str = Field(..., description="The model to use for completion")
    messages: List[Message] = Field(..., description="The conversation history")
    temperature: Optional[float] = Field(0.7, description="Sampling temperature (0-2)")
    max_tokens: Optional[int] = Field(
        512, description="Maximum number of tokens to generate"
    )
    top_p: Optional[float] = Field(None, description="Nucleus sampling parameter")
    n: Optional[int] = Field(1, description="Number of completions to generate")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")
    stop: Optional[List[str]] = Field(None, description="Stop sequences")
    presence_penalty: Optional[float] = Field(0.0, description="Presence penalty")
    frequency_penalty: Optional[float] = Field(0.0, description="Frequency penalty")
    logit_bias: Optional[Dict[str, float]] = Field(None, description="Logit bias")
    user: Optional[str] = Field(None, description="Unique user identifier")


class Choice(BaseModel):
    """
    Choice model representing a single completion choice.
    """

    index: int = Field(..., description="The index of the choice")
    message: Message = Field(..., description="The message content")
    finish_reason: Optional[str] = Field(
        None, description="The reason the generation stopped"
    )


class ChatCompletionResponse(BaseModel):
    """
    OpenAI-compatible chat completion response model.
    """

    id: str = Field(..., description="Unique identifier for the response")
    object: str = Field("chat.completion", description="The object type")
    created: int = Field(..., description="Timestamp of response creation")
    model: str = Field(..., description="The model used for completion")
    choices: List[Choice] = Field(..., description="The completion choices")
    usage: Optional[Dict[str, int]] = Field(None, description="Token usage information")


class ConversationTurn(BaseModel):
    """
    Database model for conversation turns.
    """

    id: int
    conversation_id: int
    role: str
    content: str
    message_hash: Optional[str] = None
    tokens: Optional[int] = None
    satisfaction_score: Optional[str] = None
    satisfaction_confidence: Optional[float] = None
    created_at: datetime
    extra_data: Optional[Dict[str, Any]] = None
    model_config = {"from_attributes": True}


class Conversation(BaseModel):
    """
    Database model for conversations.
    """

    id: int
    session_id: str
    created_at: datetime
    updated_at: datetime
    model: str
    total_tokens: Optional[int] = None
    extra_data: Optional[Dict[str, Any]] = None
    model_config = {"from_attributes": True}


class ConversationCreate(BaseModel):
    """
    Schema for creating a new conversation.
    """

    model: str
    user_id: Optional[str] = None


class ConversationUpdate(BaseModel):
    """
    Schema for updating a conversation.
    """

    model: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    extra_data: Optional[Dict[str, Any]] = None
