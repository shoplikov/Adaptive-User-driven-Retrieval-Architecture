from sentence_transformers import CrossEncoder


class Reranker:
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query, documents, top_k=3):
        # Input format: list of [query, doc] pairs
        pairs = [[query, doc["content"]] for doc in documents]
        scores = self.model.predict(pairs)

        # Sort by score
        scored_docs = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, score in scored_docs[:top_k]]
