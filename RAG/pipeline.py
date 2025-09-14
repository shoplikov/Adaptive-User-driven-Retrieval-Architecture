import os
import json
import faiss
import sys

sys.modules["torchvision"] = None
sys.modules["timm"] = None

import numpy as np
import ijson
import torch
from sentence_transformers import SentenceTransformer
from RAG.reranker import Reranker


class RAG:
    def __init__(
        self,
        docs_path="RAG/documents.json",
        embedding_model="all-MiniLM-L6-v2",
        index_path="rag.index",
        meta_path="rag_meta.json",
        batch_size=32,
        force_rebuild=False,
    ):

        # Auto-detect GPU for embeddings
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[RAG] Using device for embeddings: {device.upper()}")
        self.embedding_model = SentenceTransformer(embedding_model, device=device)

        self.index_path = index_path
        self.meta_path = meta_path
        self.docs_path = docs_path
        self.batch_size = batch_size

        # Load or build index
        if (
            not force_rebuild
            and os.path.exists(index_path)
            and os.path.exists(meta_path)
        ):
            print("[RAG] Loading existing FAISS index & metadata...")
            self.index = faiss.read_index(index_path)
            with open(meta_path, "r", encoding="utf-8") as f:
                self.docs = json.load(f)
        else:
            print("[RAG] Building FAISS index from documents...")
            self.docs = []
            self.index = self._build_index()
            faiss.write_index(self.index, index_path)
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(self.docs, f, ensure_ascii=False, indent=2)

    def _stream_docs(self):
        """Yield documents from JSON file without loading all into memory."""
        with open(self.docs_path, "r", encoding="utf-8") as f:
            for doc in ijson.items(f, "item"):
                yield doc

    def _build_index(self):
        dim = None
        index = None
        batch = []
        for doc in self._stream_docs():
            self.docs.append(doc)
            batch.append(doc["content"])

            if len(batch) >= self.batch_size:
                batch_embeddings = self.embedding_model.encode(
                    batch, convert_to_numpy=True, show_progress_bar=True
                )
                if index is None:
                    dim = batch_embeddings.shape[1]
                    index = faiss.IndexFlatL2(dim)
                index.add(batch_embeddings)
                batch.clear()

        # Handle last batch
        if batch:
            batch_embeddings = self.embedding_model.encode(
                batch, convert_to_numpy=True, show_progress_bar=True
            )
            if index is None:
                dim = batch_embeddings.shape[1]
                index = faiss.IndexFlatL2(dim)
            index.add(batch_embeddings)

        return index

    def retrieve(self, query, top_k=3):
        query_emb = self.embedding_model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_emb, top_k)
        return [self.docs[i] for i in indices[0]]

    def query(self, query, use_reranker=True, top_k=3):
        retrieved_docs = self.retrieve(query, top_k=top_k)
        if use_reranker:
            reranker = Reranker()
            return reranker.rerank(query, retrieved_docs)
        return retrieved_docs


if __name__ == "__main__":
    rag = RAG(force_rebuild=False)  # set to True if you add new docs

    query = "How do I beekep better?"
    results = rag.query(query)

    print(f"Query: {query}\n")
    for i, doc in enumerate(results, 1):
        print(f"{i}. {doc['title']} - {doc['content'][:200]}...\n")
