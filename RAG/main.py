import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from RAG.reranker import Reranker

class RAG:
    def __init__(self, docs_path="documents.json", embedding_model="all-MiniLM-L6-v2"):
        self.embedding_model = SentenceTransformer(embedding_model)
        self.docs = self._load_docs(docs_path)
        self.index, self.doc_embeddings = self._build_index()

    def _load_docs(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_index(self):
        # Encode documents
        embeddings = self.embedding_model.encode(
            [doc["content"] for doc in self.docs],
            convert_to_numpy=True
        )
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)
        return index, embeddings

    def retrieve(self, query, top_k=3):
        query_emb = self.embedding_model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_emb, top_k)
        return [self.docs[i] for i in indices[0]]

    def query(self, query, use_reranker=True):
        # Step 1: Retrieve
        retrieved_docs = self.retrieve(query, top_k=3)

        # Step 2: Rerank
        if use_reranker:
            reranker = Reranker()
            reranked_docs = reranker.rerank(query, retrieved_docs)
            return reranked_docs
        return retrieved_docs

if __name__ == "__main__":
    rag = RAG()
    query = "How do I beekep better?"
    results = rag.query(query)

    print(f"Query: {query}\n")
    for i, doc in enumerate(results, 1):
        if i > 5:
            break
        print(f"{i}. {doc['title']} - {doc['content']}")
