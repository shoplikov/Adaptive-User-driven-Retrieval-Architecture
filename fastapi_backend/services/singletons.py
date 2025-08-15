# services/singletons.py
import threading
from config import settings
from RAG.main import RAG
from wildfeedback.praise import PraisePipeline

_rag = None
_feedback = None
_lock = threading.Lock()

def get_rag():
    global _rag
    if _rag is None:
        with _lock:
            if _rag is None:
                _rag = RAG(docs_path=settings.RAG_DOCS_PATH)
    return _rag

def get_feedback():
    global _feedback
    if _feedback is None:
        with _lock:
            if _feedback is None:
                _feedback = PraisePipeline(
                    strategy_file=settings.FEEDBACK_STRATEGY_PATH,
                    classifier_file=settings.FEEDBACK_CLASSIFIER_PATH
                )
    return _feedback
