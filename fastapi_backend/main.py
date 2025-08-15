#!/usr/bin/env python3
"""
FastAPI backend for AURA chatbot with OpenAI-compatible API endpoint.
"""

import os
import logging
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from pydantic import ValidationError
from typing import List, Optional

# Import custom modules
from models.schemas import ChatCompletionRequest, ChatCompletionResponse
from services.chat_completion import ChatCompletionService
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

# Initialize chat completion service
chat_service = ChatCompletionService()

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: Request, payload: ChatCompletionRequest):
    """
    OpenAI-compatible chat completion endpoint.
    Accepts POST requests with chat completion format including messages array,
    model parameter, temperature, max_tokens, and stream options.
    """
    try:
        # Process the chat completion request
        response = chat_service.process_request(payload)
        return response
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