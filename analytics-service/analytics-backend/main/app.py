"""Main application entry point for analytics service"""
import os
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Import custom modules
from models.database import get_db, init_db
from models.schemas import (
    AnalyticsResponse,
    MetricsOverview,
    SatisfactionMetrics,
    TokenUsage,
    StatusBreakdown,
)
from services.analytics_service import AnalyticsService
from config.settings import settings
from api.analytics import router as analytics_router

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="AURA Analytics API",
    description="Read-only analytics endpoints for AURA conversation metrics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
analytics_service = AnalyticsService()

# Include analytics router
app.include_router(analytics_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    init_db()


@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Health check endpoint to verify service status.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get(
    "/api/v1/analytics/metrics/overview",
    response_model=AnalyticsResponse[MetricsOverview],
)
async def get_metrics_overview(db: Session = Depends(get_db)):
    """
    Get comprehensive overview of all key metrics.
    """
    try:
        metrics = analytics_service.get_metrics_overview(db)
        return AnalyticsResponse(
            status="success",
            data=metrics,
            timestamp=datetime.utcnow().isoformat(),
            cache_ttl=300,
        )
    except Exception as e:
        logging.error(f"Error fetching metrics overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@app.get(
    "/api/v1/analytics/metrics/conversations",
    response_model=AnalyticsResponse[Dict[str, int]],
)
async def get_conversation_counts(db: Session = Depends(get_db)):
    """
    Get total conversation counts and status breakdown.
    """
    try:
        counts = analytics_service.get_conversation_counts(db)
        return AnalyticsResponse(
            status="success",
            data=counts,
            timestamp=datetime.utcnow().isoformat(),
            cache_ttl=300,
        )
    except Exception as e:
        logging.error(f"Error fetching conversation counts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@app.get(
    "/api/v1/analytics/metrics/satisfaction",
    response_model=AnalyticsResponse[SatisfactionMetrics],
)
async def get_satisfaction_metrics(db: Session = Depends(get_db)):
    """
    Get satisfaction score breakdown and percentages.
    """
    try:
        satisfaction = analytics_service.get_satisfaction_metrics(db)
        return AnalyticsResponse(
            status="success",
            data=satisfaction,
            timestamp=datetime.utcnow().isoformat(),
            cache_ttl=300,
        )
    except Exception as e:
        logging.error(f"Error fetching satisfaction metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@app.get(
    "/api/v1/analytics/metrics/tokens", response_model=AnalyticsResponse[TokenUsage]
)
async def get_token_usage(db: Session = Depends(get_db)):
    """
    Get token usage statistics.
    """
    try:
        tokens = analytics_service.get_token_usage(db)
        return AnalyticsResponse(
            status="success",
            data=tokens,
            timestamp=datetime.utcnow().isoformat(),
            cache_ttl=300,
        )
    except Exception as e:
        logging.error(f"Error fetching token usage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@app.get(
    "/api/v1/analytics/metrics/status",
    response_model=AnalyticsResponse[StatusBreakdown],
)
async def get_status_breakdown(db: Session = Depends(get_db)):
    """
    Get conversation status breakdown.
    """
    try:
        status_breakdown = analytics_service.get_status_breakdown(db)
        return AnalyticsResponse(
            status="success",
            data=status_breakdown,
            timestamp=datetime.utcnow().isoformat(),
            cache_ttl=300,
        )
    except Exception as e:
        logging.error(f"Error fetching status breakdown: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@app.get(
    "/api/v1/analytics/metrics/trends", response_model=AnalyticsResponse[Dict[str, Any]]
)
async def get_trends(db: Session = Depends(get_db), period: str = "daily"):
    """
    Get time-based trends for conversations.
    """
    try:
        trends = analytics_service.get_trends(db, period)
        return AnalyticsResponse(
            status="success",
            data=trends,
            timestamp=datetime.utcnow().isoformat(),
            cache_ttl=300,
        )
    except Exception as e:
        logging.error(f"Error fetching trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Welcome to the Analytics Service"}


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level=settings.LOG_LEVEL)
