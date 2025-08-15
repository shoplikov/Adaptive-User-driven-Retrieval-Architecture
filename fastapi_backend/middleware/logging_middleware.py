"""
Request logging middleware for FastAPI.
"""

import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime

class LogRequestMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging incoming requests and responses.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Log the request and response.
        """
        # Log request
        logging.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host}:{request.client.port}"
        )

        # Process the request
        response = await call_next(request)

        # Log response
        logging.info(
            f"Response: {response.status_code} "
            f"to {request.client.host}:{request.client.port} "
            f"in {response.headers.get('X-Response-Time', 'N/A')}"
        )

        return response