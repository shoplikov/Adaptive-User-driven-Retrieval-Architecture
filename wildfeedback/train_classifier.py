import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
from praise import PraisePipeline

# Load labeled data
with open("data/satisfaction_labels.json", "r", encoding="utf-8") as f:
    labeled_data = json.load(f)
print(f"Loaded {len(labeled_data)} labeled examples.")
pipeline = PraisePipeline("data/strategies.json")

# Build training features
X = []
y = []
for row in labeled_data:
    sim_features = pipeline.compute_similarity_features(row["user_message"])
    X.append(sim_features)
    y.append(row["label"])

X = np.array(X)
y = np.array(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
clf = LogisticRegression(max_iter=500, multi_class="ovr")
clf.fit(X_train, y_train)

print(classification_report(y_test, clf.predict(X_test)))

joblib.dump(clf, "praise_classifier.pkl")
