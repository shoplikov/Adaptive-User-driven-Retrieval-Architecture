#!/usr/bin/env python3
"""
FastAPI backend for AURA chatbot with OpenAI-compatible API endpoint.
"""

import os
import logging
from fastapi import FastAPI, Request, HTTPException, status, Query, Path, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Response, Header
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from pydantic import ValidationError
from typing import List, Optional

# Import custom modules
from models.schemas import ChatCompletionRequest, ChatCompletionResponse, Message, Conversation as ConversationSchema, ConversationTurn as ConversationTurnSchema, ConversationCreate, ConversationUpdate
from services.chat_completion import ChatCompletionService
from services.conversation_service import ConversationService
from config import settings
from middleware.logging_middleware import LogRequestMiddleware
from middleware.conversation_middleware import ConversationMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="AURA Chat API",
    description="OpenAI-compatible chat completion API for AURA chatbot",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(LogRequestMiddleware)
app.add_middleware(ConversationMiddleware)

# Initialize services
chat_service = ChatCompletionService()
conversation_service = ConversationService()


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: Request,
    payload: ChatCompletionRequest,
    response: Response,
    x_session_id: Optional[str] = Header(
        default=None,
        alias="X-Conversation-Session-ID",
        description="Conversation session/thread ID. If omitted, the server falls back to payload.session_id, then payload.user."
    ),
):
    try:
        session_id = x_session_id or getattr(payload, "session_id", None) or payload.user
        conversation = conversation_service.get_or_create_conversation(
            session_id=session_id,
            model=payload.model
        )
        response.headers["X-Conversation-Id"] = str(conversation.id)
        response.headers["X-Conversation-Session-ID"] = conversation.session_id
        reply = chat_service.process_request(payload, conversation_id=conversation.id)
        return reply
    except Exception as e:
        logging.error(f"Error processing chat completion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get("/health", response_model=dict)
async def health_check():
    """
    Health check endpoint to verify service status.
    """
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/v1/models", response_model=List[str])
async def list_models():
    """
    List available models.
    """
    return [settings.DEFAULT_MODEL]

@app.post("/v1/conversations", response_model=ConversationSchema)
async def create_conversation(request: Request, model: str = Query(..., description="Model to use for the conversation")):
    """
    Create a new conversation.
    """
    try:
        conversation = conversation_service.create_conversation(model=model)
        return conversation
    except Exception as e:
        logging.error(f"Error creating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get("/v1/conversations/{conversation_id}", response_model=ConversationSchema)
async def get_conversation(conversation_id: int = Path(..., description="ID of the conversation to retrieve", gt=0)):
    """
    Get conversation details by ID.
    """
    try:
        conversation = conversation_service.get_conversation_by_id(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        return conversation
    except Exception as e:
        logging.error(f"Error retrieving conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get("/v1/conversations/{conversation_id}/messages", response_model=List[ConversationTurnSchema])
async def get_conversation_history(conversation_id: int = Path(..., description="ID of the conversation to get history for", gt=0)):
    """
    Get message history for a conversation.
    """
    try:
        history = conversation_service.get_conversation_history(conversation_id)
        return history
    except Exception as e:
        logging.error(f"Error retrieving conversation history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/v1/conversations/{conversation_id}/messages", response_model=ConversationTurnSchema)
async def add_message_to_conversation(
    conversation_id: int = Path(..., description="ID of the conversation to add message to", gt=0),
    message: Message = Body(..., description="Message to add to the conversation")
):
    """
    Add a message to an existing conversation.
    """
    try:
        turn = conversation_service.add_message_to_conversation(conversation_id, message)
        return turn
    except Exception as e:
        logging.error(f"Error adding message to conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.put("/v1/conversations/{conversation_id}", response_model=ConversationSchema)
async def update_conversation(
    conversation_id: int = Path(..., description="ID of the conversation to update", gt=0),
    update_data: ConversationUpdate = Body(..., description="Data to update the conversation with")
):
    """
    Update a conversation.
    """
    try:
        conversation = conversation_service.update_conversation(conversation_id, update_data)
        return conversation
    except Exception as e:
        logging.error(f"Error updating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.delete("/v1/conversations/{conversation_id}", response_model=bool)
async def delete_conversation(conversation_id: int = Path(..., description="ID of the conversation to delete", gt=0)):
    """
    Delete a conversation.
    """
    try:
        return conversation_service.delete_conversation(conversation_id)
    except Exception as e:
        logging.error(f"Error deleting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Custom error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors with detailed error messages.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """
    Handle Pydantic validation errors.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=settings.LOG_LEVEL)
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )