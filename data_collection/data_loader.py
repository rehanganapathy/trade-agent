# -----------------------------
# Data Loading Module
# -----------------------------

import json
from config import hts_json_path


def load_hts_data():
    """Load and preprocess HTS data."""
    with open(hts_json_path, "r", encoding="utf-8") as f:
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

    return hs_entries
