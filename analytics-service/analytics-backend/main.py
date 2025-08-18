#!/usr/bin/env python3
"""
FastAPI backend for AURA Analytics Service - Read-only analytics endpoints
"""
import os
import logging
from fastapi import FastAPI
import uvicorn

# Import the main app from the main.app module
from main.app import app

if __name__ == "__main__":
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    uvicorn.run(
        "main.app:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8001")),
        reload=True,
        log_level=os.getenv("LOG_LEVEL", "INFO").lower(),
    )
