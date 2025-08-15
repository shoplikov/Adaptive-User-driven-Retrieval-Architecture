# AURA Chat API Deployment Guide

This guide provides instructions for deploying the AURA Chat API backend.

## Prerequisites

1. Python 3.8+
2. PostgreSQL database
3. LMStudio API endpoint running
4. Required Python packages (see `requirements.txt`)

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Database configuration
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=your_db_name
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# LMStudio configuration
LMSTUDIO_ENDPOINT=http://localhost:1234/v1/chat/completions
DEFAULT_MODEL=hermes-3-llama-3.2-3b

# Application settings
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info
```

## Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Initialize the database:
   ```bash
   python -m fastapi_backend.migrations create
   ```

## Running the Server

### Development Mode
```bash
python fastapi_backend/scripts/start_server.py
```

### Production Mode
```bash
uvicorn fastapi_backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Chat Completion
- **POST** `/v1/chat/completions`
  - OpenAI-compatible chat completion endpoint
  - Accepts JSON body with `messages`, `model`, `temperature`, `max_tokens`, etc.

### Health Check
- **GET** `/health`
  - Returns service health status

### Models
- **GET** `/v1/models`
  - Returns list of available models

## Testing

Run tests with:
```bash
pytest tests/
```

## Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t aura-chat-api .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 -e POSTGRES_USER=your_user -e POSTGRES_PASSWORD=your_password aura-chat-api
   ```

## Troubleshooting

1. **Database connection issues**: Verify PostgreSQL is running and credentials are correct.
2. **LMStudio endpoint errors**: Ensure LMStudio is running and accessible at the configured endpoint.
3. **Permission errors**: Check file permissions, especially for the `.env` file and log files.

## Logging

Logs are written to `aura_chat_api.log` and also output to stdout.

## Updating

1. Pull latest code changes
2. Update dependencies if needed
3. Run database migrations if schema changes are present
4. Restart the server