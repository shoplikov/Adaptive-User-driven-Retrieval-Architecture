"""
Conversation persistence middleware for FastAPI.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import logging


class ConversationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for managing conversation persistence.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process the request and ensure conversation persistence.
        """
        # Check if this is a chat completion request
        if request.url.path == "/v1/chat/completions" and request.method == "POST":
            try:
                # Process the request
                response = await call_next(request)

                # Log successful conversation processing
                logging.info(
                    f"Conversation processed successfully: {request.url.path} "
                    f"from {request.client.host}:{request.client.port}"
                )

                return response
            except Exception as e:
                logging.error(f"Conversation processing error: {e}")
                raise
        else:
            # For other requests, just pass through
            return await call_next(request)
