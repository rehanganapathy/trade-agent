# -----------------------------
# Embedding Generation Module
# -----------------------------

from sentence_transformers import SentenceTransformer


def generate_embeddings(hs_entries, model_name='all-MiniLM-L6-v2'):
    """Generate embeddings for all HS descriptions using sentence-transformers."""
    print(f"Loading embedding model: {model_name}...")
    model = SentenceTransformer(model_name)
    print("Model loaded!")

    print("Generating embeddings for all HS descriptions... (may take some time)")

    descriptions = [entry["description"] for entry in hs_entries]
    embeddings = model.encode(descriptions, show_progress_bar=True)

    for entry, embedding in zip(hs_entries, embeddings):
        entry["embedding"] = embedding.tolist()

    print("Embeddings ready!")
    return hs_entries
