# Use official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Expose the port the app runs on
EXPOSE 8001

# Command to run the application
CMD ["python", "-m", "uvicorn", "main.app:app", "--host", "0.0.0.0", "--port", "8001"]