from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from RAG.pipeline import RAG
from wildfeedback.praise import PraisePipeline

# --- Config ---
LMSTUDIO_ENDPOINT = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "my-model"  # replace with your LM Studio model ID
STRATEGY_PATH = os.path.join("wildfeedback", "data", "strategies.json")
CLASSIFIER_PATH = os.path.join("wildfeedback", "praise_classifier.pkl")

# --- Load pipelines ---
rag = RAG(docs_path=os.path.join("RAG", "documents.json"))
feedback = PraisePipeline(STRATEGY_PATH, CLASSIFIER_PATH)

# --- FastAPI app ---
app = FastAPI()

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {"status": "API is running"}


@app.post("/chat")
def chat(req: ChatRequest):
    user_msg = req.message.strip()

    # 1) RAG retrieval
    docs = rag.query(user_msg)
    context = "\n".join([doc["content"] for doc in docs]) if docs else "No context found."
    prompt = f"[CONTEXT]\n{context}\n[USER]\n{user_msg}"

    # 2) Call LM Studio
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 512,
        "temperature": 0.7,
    }

    try:
        resp = requests.post(LMSTUDIO_ENDPOINT, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        reply = data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        reply = f"[Error contacting LM Studio: {e}]"

    # 3) Feedback classifier
    try:
        feedback_result = feedback.classify(user_msg)
        sat_dsat = max(feedback_result, key=feedback_result.get)
    except Exception:
        sat_dsat = "Unknown"

    return {
        "user": user_msg,
        "reply": reply,
        "feedback": sat_dsat,
        "retrieved_docs": docs,
    }
