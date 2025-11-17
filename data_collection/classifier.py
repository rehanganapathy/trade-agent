# -----------------------------
# Classification Module
# -----------------------------

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Initialize embedding model (singleton pattern)
_embedding_model = None


def get_embedding_model():
    """Get or create the embedding model singleton."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model


def classify_hs(product_description, hs_entries, top_n=5):
    """Classify product description to HS codes using semantic similarity."""
    model = get_embedding_model()

    # Generate embedding for input
    desc_embedding = model.encode([product_description])[0]

    # Compute cosine similarity with all HS descriptions
    similarities = []
    for entry in hs_entries:
        sim = cosine_similarity(
            np.array(desc_embedding).reshape(1, -1),
            np.array(entry["embedding"]).reshape(1, -1)
        )[0][0]
        similarities.append((entry["htsno"], entry["description"], sim))

    # Sort by similarity
    similarities.sort(key=lambda x: x[2], reverse=True)

    # Return top N
    return similarities[:top_n]
