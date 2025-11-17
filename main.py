"""Main entry point for HS code classification system."""
from data_collection.data_loader import load_hts_data
from data_collection.classifier import classify_hs
from embedding_generator import generate_embeddings
import json
from config import hts_json_path

# -----------------------------
# 2️⃣ Load HTS Data
# -----------------------------


def load_hts_data():
    with open(HTS_JSON_PATH, "r", encoding="utf-8") as f:
        hts_data = json.load(f)

    # Extract HS codes and descriptions
    hs_entries = [
        {
            "htsno": item.get("htsno"),
            "description": item.get("description", "")
        }
        for item in hts_data
        if item.get("description")
    ]

    print(f"Loaded {len(hs_entries)} HS entries.")
    return hs_entries

# -----------------------------
# 3️⃣ Generate Embeddings
# -----------------------------


def generate_embeddings(hs_entries):
    # Precompute embeddings for all HS descriptions
    print("Generating embeddings for all HS descriptions... (may take some time)")

    for entry in hs_entries:
        entry["embedding"] = openai.Embedding.create(
            model="text-embedding-3-large",
            input=entry["description"]
        )["data"][0]["embedding"]

    print("Embeddings ready!")
    return hs_entries

# -----------------------------
# 4️⃣ Classification Function
# -----------------------------


def classify_hs(product_description, hs_entries, top_n=5):
    # Generate embedding for input
    desc_embedding = openai.Embedding.create(
        model="text-embedding-3-large",
        input=product_description
    )["data"][0]["embedding"]

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

# -----------------------------
# Main Script
# -----------------------------


if __name__ == "__main__":
    # Load HTS data
    hs_entries = load_hts_data()

    # Generate embeddings
    hs_entries = generate_embeddings(hs_entries)

    # Test the classifier
    product = "Laptop backpack with padded compartment"
    results = classify_hs(product, hs_entries, top_n=5)

    print(f"\nTop HS code suggestions for: '{product}'\n")
    for code, desc, score in results:
        print(f"HS Code: {code} | Score: {score:.4f}")
        print(f"Description: {desc}\n")
