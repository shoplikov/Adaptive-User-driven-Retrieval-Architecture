import json
from sentence_transformers import SentenceTransformer, util
import numpy as np
import joblib


class PraisePipeline:
    def __init__(self, strategy_file, classifier_file=None):
        # Load strategies
        with open(strategy_file, "r", encoding="utf-8") as f:
            self.strategies = json.load(f)

        # Load embedding model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # Precompute embeddings for strategies
        self.strategy_embeddings, self.strategy_labels = self._embed_strategies()

        # Load classifier if provided
        self.classifier = joblib.load(classifier_file) if classifier_file else None

    def _embed_strategies(self):
        texts = []
        labels = []
        for label, phrases in self.strategies.items():
            for phrase in phrases:
                texts.append(phrase)
                labels.append(label)
        embeddings = self.model.encode(
            texts, convert_to_tensor=True, normalize_embeddings=True
        )
        return embeddings, labels

    def compute_similarity_features(self, text):
        # Embed user message
        user_emb = self.model.encode(
            text, convert_to_tensor=True, normalize_embeddings=True
        )
        # Compute cosine similarity
        similarities = util.cos_sim(user_emb, self.strategy_embeddings)[0].cpu().numpy()
        return similarities

    def classify(self, text):
        # Return soft probabilities using trained classifier
        if not self.classifier:
            raise RuntimeError("Classifier not loaded.")
        features = self.compute_similarity_features(text).reshape(1, -1)
        probs = self.classifier.predict_proba(features)[0]
        return dict(zip(self.classifier.classes_, probs))


# Example usage
if __name__ == "__main__":
    pipeline = PraisePipeline("data/strategies.json", "praise_classifier.pkl")
    msg = "That answer doesn’t help at all!"
    print(pipeline.classify(msg))
