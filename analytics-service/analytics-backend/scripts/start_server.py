#!/usr/bin/env python3
"""Script to start the analytics service server"""
import os
import sys
import subprocess
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main function to start the server"""
    try:
        # Change to the project directory
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_dir)

        # Load environment variables from .env file
        env_path = os.path.join(project_dir, ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
            logger.info(f"Loaded environment variables from {env_path}")
            logger.info(
                f"ANALYTICS_DATABASE_URL: {os.getenv('ANALYTICS_DATABASE_URL')}"
            )

        # Install dependencies if requirements.txt exists
        requirements_path = os.path.join(project_dir, "requirements.txt")
        if os.path.exists(requirements_path):
            logger.info("Installing dependencies...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-r", requirements_path]
            )
        else:
            logger.warning(
                "No requirements.txt found. Skipping dependency installation."
            )

        # Start the server
        logger.info("Starting analytics service server...")
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "main.app:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8001",
            ]
        )

    except subprocess.CalledProcessError as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
