# -----------------------------
# Configuration Module
# -----------------------------
import os
from pathlib import Path

# Groq API Key - load from environment
groq_api_key = os.getenv("GROQ_API_KEY", "")

# Groq Model (default to llama models available on Groq)
groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Path to HTS JSON file downloaded from USITC
hts_json_path = os.getenv("HTS_JSON_PATH", "hts_current.json")

# Vector DB configuration
chroma_persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
