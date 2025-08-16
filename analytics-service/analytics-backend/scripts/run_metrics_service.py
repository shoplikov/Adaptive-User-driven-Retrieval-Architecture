#!/usr/bin/env python3
"""
Script to run the metrics service periodically.
"""
import os
import sys
import time
import logging
from datetime import datetime
import schedule

# Add the analytics-backend directory to Python path
analytics_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, analytics_backend_dir)

# Add fastapi_backend directory for cross-service imports
fastapi_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'fastapi_backend'))
sys.path.insert(0, fastapi_backend_dir)

from services.metrics_service import MetricsService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('metrics_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_periodic_task():
    """Run the periodic metrics task."""
    logger.info("Running periodic metrics task")
    try:
        # Initialize and run the metrics service
        metrics_service = MetricsService()
        metrics_service.run_periodic_task()
    except Exception as e:
        logger.error(f"Error running periodic task: {e}")

if __name__ == "__main__":
    logger.info("Starting metrics service")

    # Set up periodic execution (every 10 minutes)
    schedule.every(10).minutes.do(run_periodic_task)

    # Run the first task immediately
    run_periodic_task()

    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(1)