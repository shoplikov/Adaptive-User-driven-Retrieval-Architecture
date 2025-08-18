# AURA Chat API - FastAPI Backend

![AURA Chat API Logo](https://example.com/logo.png)

**OpenAI-compatible chat completion API with advanced RAG and feedback systems**

## Overview

AURA Chat API is a powerful, production-ready FastAPI backend that provides an OpenAI-compatible chat completion interface with advanced features:


## Table of Contents

- [Quick Start](#quick-start)
- [API Reference](#api-reference)
  - [Chat Completion](#chat-completion)
  - [Health Check](#health-check)
  - [Models Endpoint](#models-endpoint)
- [Configuration](#configuration)
- [Deployment](#deployment)
  - [Docker](#docker)
  - [Local Development](#local-development)
- [RAG System](#rag-system)
- [Feedback Analysis](#feedback-analysis)
- [Contributing](#contributing)

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL database
- LMStudio API endpoint running

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/aura-chat-api.git
   cd aura-chat-api
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables (create `.env` file):
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
   LOG_LEVEL=INFO
   ```

4. Initialize the database:
   ```bash
   python -m fastapi_backend.migrations create
   ```

5. Start the server:
   ```bash
   python fastapi_backend/scripts/start_server.py
   ```

### Docker Deployment

```bash
# Build the Docker image
docker build -t aura-chat-api .

# Run the container
docker run -p 8000:8000 \
  -e POSTGRES_USER=your_user \
  -e POSTGRES_PASSWORD=your_password \
  aura-chat-api
```

## API Reference

### Chat Completion

**Endpoint:** `POST /v1/chat/completions`

OpenAI-compatible chat completion endpoint. Accepts standard OpenAI chat format.

**Request Body:**
```json
{
  "model": "hermes-3-llama-3.2-3b",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What's the weather like today?"}
  ],
  "temperature": 0.7,
  "max_tokens": 512
}
```

**Response:**
```json
{
  "id": "chatcmpl-12345",
  "object": "chat.completion",
  "created": 1698745600,
  "model": "hermes-3-llama-3.2-3b",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The weather is sunny with a high of 75°F."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 12,
    "total_tokens": 27
  }
}
```

### Health Check

**Endpoint:** `GET /health`

Returns service health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Models Endpoint

**Endpoint:** `GET /v1/models`

Returns list of available models.

**Response:**
```json
[
  "hermes-3-llama-3.2-3b"
]
```

## RAG System

The Retrieval-Augmented Generation (RAG) system enhances responses by:

1. **Document Retrieval**: Searches through indexed documents using FAISS
2. **Context Enrichment**: Provides relevant context to the AI model
3. **Improved Accuracy**: Delivers more accurate and relevant responses

## Feedback Analysis

The feedback system automatically analyzes user satisfaction by:

1. **Sentiment Detection**: Classifies user responses as positive, negative, or neutral
2. **Continuous Learning**: Improves response quality over time
3. **Actionable Insights**: Provides feedback to improve the AI model

## Configuration

All configuration is done through environment variables. See the [.env.example](.env.example) file for details.

## Deployment

### Docker

For production deployment, use Docker:

```bash
# Build and run with docker-compose
docker compose up --build -d
```

### Local Development

For development:

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python fastapi_backend/scripts/start_server.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please contact [support@example.com](mailto:support@example.com).

---

**AURA Chat API** - Empowering Conversational AI with Advanced Retrieval and Feedback Systems