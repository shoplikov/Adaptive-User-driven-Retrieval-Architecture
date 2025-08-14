# AURA

## Overview

AURA (Adaptive-User-driven-Retrieval-Architecture) is a comprehensive chatbot system with Retrieval-Augmented Generation (RAG) capabilities. It provides a FastAPI backend with a Tkinter-based chat interface, leveraging advanced NLP models for intelligent conversation and feedback analysis.

## Features

- **Retrieval-Augmented Generation (RAG)**: Advanced document retrieval using FAISS and sentence transformers
- **Feedback Analysis**: Machine learning-based satisfaction classification
- **Modular Architecture**: Separate components for API, UI, and services
- **Docker Support**: Easy deployment with Docker Compose
- **Multilingual Support**: Unicode and Cyrillic character support

## System Architecture

- **Backend**: FastAPI with SQLAlchemy ORM
- **Database**: PostgreSQL
- **LLM Integration**: OpenAI API or local LM Studio
- **Frontend**: Tkinter-based chat interface
- **RAG System**: FAISS index with sentence transformers
- **Feedback System**: ML-based classification with scikit-learn

## Prerequisites

1. **PostgreSQL Database** - Either local installation or use the Docker setup
2. **OpenAI API Key** - For LLM functionality (or configure for local LM Studio)
3. **Python 3.8+** with the required packages
4. **RAG Documents** - The RAG/documents.json file

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/aura.git
cd aura
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file with your configuration:

```bash
cp .env.example .env
```

Edit the `.env` file with your database and API credentials:

```ini
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=aura_chatbot
LLM_API_KEY=your_openai_api_key
```

## Running the Application

### Option 1: Local Development

#### 1. Start the FastAPI Server

```bash
# Run the FastAPI server
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Run the Chat Interface

```bash
# Run the UI application
python ui.py
```

### Option 2: Docker (Recommended)

```bash
# Create .env file with required variables
echo "POSTGRES_USER=postgres" >> .env
echo "POSTGRES_PASSWORD=password" >> .env
echo "POSTGRES_DB=aura_chatbot" >> .env

# Run with Docker Compose
cd docker
docker-compose up --build
```

## API Endpoints

The FastAPI backend provides the following endpoints:

- **Conversations**: `/conversations` - Manage chat conversations
- **Feedback**: `/feedback` - Submit and retrieve feedback
- **Documents**: `/documents` - Manage documents for RAG
- **LLM**: `/llm` - Configure and use language models
- **Metrics**: `/metrics` - Track system performance
- **System**: `/system` - System configuration

## UI Configuration

The chat interface (`ui.py`) connects to:
- **LM Studio Endpoint**: `http://localhost:1234` (default)
- **RAG System**: Uses local RAG/documents.json
- **Feedback Classifier**: Uses wildfeedback/praise_classifier.pkl

## Development

### Database Migrations

The application uses SQLAlchemy for database operations. To initialize the database:

```bash
python -c "from src.config.database import init_db; init_db()"
```

### Testing

The application includes comprehensive testing capabilities. To run tests:

```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [Sentence Transformers](https://www.sbert.net/)
- [scikit-learn](https://scikit-learn.org/)
- [OpenAI](https://www.openai.com/)
