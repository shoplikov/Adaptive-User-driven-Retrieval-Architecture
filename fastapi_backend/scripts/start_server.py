#!/usr/bin/env python3
"""
Startup script for AURA Chat API
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def main():
    # Get the root directory
    root_dir = Path(__file__).resolve().parent.parent

    # Change working directory
    os.chdir(root_dir)

    # Check if Docker is available
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        has_docker = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        has_docker = False

    # Check if docker-compose is available
    try:
        subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
        has_docker_compose = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        has_docker_compose = False

    # Check if we should use Docker
    use_docker = has_docker and has_docker_compose

    if use_docker:
        print("Starting AURA Chat API with Docker...")
        try:
            # Build and start the containers
            subprocess.run(["docker-compose", "up", "--build", "-d"], check=True)
            print("AURA Chat API is running in Docker containers.")
            print("Access the API at http://localhost:8000")
            print("Access the PostgreSQL database at http://localhost:5432")
            return
        except subprocess.CalledProcessError as e:
            print(f"Error starting Docker containers: {e}")
            sys.exit(1)
    else:
        print("Starting AURA Chat API directly...")

        # Install dependencies
        print("Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

        # Start the FastAPI server
        print("Starting FastAPI server...")
        try:
            subprocess.run(
                ["uvicorn", "fastapi_backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error starting FastAPI server: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()