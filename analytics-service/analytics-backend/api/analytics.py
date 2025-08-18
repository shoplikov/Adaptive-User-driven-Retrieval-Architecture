"""Analytics API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from services.database import DatabaseService
from config.settings import settings

# Debug logging
import logging

logger = logging.getLogger(__name__)
logger.info(f"Settings module: {settings}")
logger.info(f"Settings attributes: {dir(settings)}")

router = APIRouter()


def get_db_service() -> DatabaseService:
    """Dependency to get database service"""
    try:
        return DatabaseService(settings.ANALYTICS_DATABASE_URL)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database connection error: {str(e)}"
        )


@router.get("/metrics/total_conversations", response_model=Dict[str, int])
def get_total_conversations(
    db: DatabaseService = Depends(get_db_service),
) -> Dict[str, int]:
    """
    Get total number of conversations

    Returns:
        Dictionary with 'total' key containing the count
    """
    try:
        total = db.get_total_conversations()
        return {"total": total}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving total conversations: {str(e)}"
        )


@router.get("/metrics/satisfaction", response_model=Dict[str, int])
def get_satisfaction_stats(
    db: DatabaseService = Depends(get_db_service),
) -> Dict[str, int]:
    """
    Get satisfaction statistics

    Returns:
        Dictionary with satisfaction levels as keys and counts as values
    """
    try:
        stats = db.get_satisfaction_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving satisfaction stats: {str(e)}"
        )


@router.get("/metrics/token_usage", response_model=Dict[str, int])
def get_token_usage(db: DatabaseService = Depends(get_db_service)) -> Dict[str, int]:
    """
    Get token usage statistics

    Returns:
        Dictionary with 'input_tokens' and 'output_tokens' counts
    """
    try:
        usage = db.get_token_usage()
        return usage
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving token usage: {str(e)}"
        )


@router.get("/metrics/status_breakdown", response_model=Dict[str, int])
def get_status_breakdown(
    db: DatabaseService = Depends(get_db_service),
) -> Dict[str, int]:
    """
    Get conversation status breakdown

    Returns:
        Dictionary with status types as keys and counts as values
    """
    try:
        breakdown = db.get_status_breakdown()
        return breakdown
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving status breakdown: {str(e)}"
        )
