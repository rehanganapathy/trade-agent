"""Integrated trade agent combining form filling with HS code classification.

This agent automatically classifies products to HS codes while filling trade forms.
"""
from typing import Dict, Any, Optional
import json
from pathlib import Path

from agent import fill_form
from data_collection.classifier import classify_hs
from data_collection.data_loader import load_hts_data
from embedding_generator import generate_embeddings
import pickle
import os


class TradeAgent:
    """Agent for automated trade form filling with HS code classification."""

    def __init__(self, hs_data_cache_path: str = "hs_data_cache.pkl"):
        """Initialize the trade agent.

        Args:
            hs_data_cache_path: Path to cache file for HS data embeddings
        """
        self.hs_data_cache_path = hs_data_cache_path
        self.hs_entries = None
        self._load_hs_data()

    def _load_hs_data(self):
        """Load or generate HS code data with embeddings."""
        if os.path.exists(self.hs_data_cache_path):
            print(f"Loading cached HS data from {self.hs_data_cache_path}...")
            with open(self.hs_data_cache_path, 'rb') as f:
                self.hs_entries = pickle.load(f)
            print(f"Loaded {len(self.hs_entries)} HS entries from cache.")
        else:
            print("Cache not found. Loading and generating HS data...")
            try:
                self.hs_entries = load_hts_data()
                self.hs_entries = generate_embeddings(self.hs_entries)

                # Cache the data for future use
                with open(self.hs_data_cache_path, 'wb') as f:
                    pickle.dump(self.hs_entries, f)
                print(f"HS data cached to {self.hs_data_cache_path}")
            except FileNotFoundError:
                print("Warning: HTS data file not found. HS code classification will be unavailable.")
                self.hs_entries = []

    def classify_product(self, product_description: str, top_n: int = 5) -> list:
        """Classify a product to HS codes.

        Args:
            product_description: Description of the product
            top_n: Number of top matches to return

        Returns:
            List of (hs_code, description, similarity_score) tuples
        """
        if not self.hs_entries:
            return []
        return classify_hs(product_description, self.hs_entries, top_n=top_n)

    def fill_trade_form(
        self,
        template: Dict[str, Any],
        prompt: str,
        use_ai: bool = True,
        auto_classify_hs: bool = True,
        db_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Fill a trade form with automatic HS code classification using LLM.

        Args:
            template: Form template dictionary
            prompt: User input text describing the trade
            use_ai: Kept for backward compatibility, always uses LLM
            auto_classify_hs: Whether to automatically classify HS codes
            db_data: Optional database data for autofill

        Returns:
            Filled form dictionary with HS codes classified
        """
        # Fill the form using LLM extraction
        filled = fill_form(template, prompt, use_openai=True, db_data=db_data)

        # If auto-classification is enabled and there's a product description
        if auto_classify_hs and self.hs_entries:
            # Look for product description field
            product_desc = None
            for key in ['product_description', 'description', 'description_of_goods', 'product_name']:
                if key in filled and filled[key]:
                    product_desc = filled[key]
                    break

            # If we found a product description and HS code field exists
            if product_desc:
                hs_results = self.classify_product(product_desc, top_n=1)
                if hs_results:
                    best_match = hs_results[0]
                    # Fill HS code if field exists and is empty
                    if 'hs_code' in filled and not filled['hs_code']:
                        filled['hs_code'] = best_match[0]
                    # Add metadata about the classification
                    filled['_hs_classification'] = {
                        'code': best_match[0],
                        'description': best_match[1],
                        'confidence': float(best_match[2])
                    }

        return filled

    def get_hs_suggestions(self, product_description: str, top_n: int = 5) -> list:
        """Get HS code suggestions for a product.

        Args:
            product_description: Product description
            top_n: Number of suggestions to return

        Returns:
            List of dictionaries with hs_code, description, and confidence
        """
        results = self.classify_product(product_description, top_n=top_n)
        return [
            {
                'hs_code': code,
                'description': desc,
                'confidence': float(score)
            }
            for code, desc, score in results
        ]


# Convenience function for direct use
def fill_trade_form_with_classification(
    template_path: str,
    prompt: str,
    use_ai: bool = True,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """Fill a trade form with automatic HS classification using LLM.

    Args:
        template_path: Path to the template JSON file
        prompt: User input describing the trade
        use_ai: Kept for backward compatibility, always uses LLM
        output_path: Optional path to save the filled form

    Returns:
        Filled form dictionary
    """
    agent = TradeAgent()

    # Load template
    with open(template_path, 'r') as f:
        template = json.load(f)

    # Fill form using LLM
    filled = agent.fill_trade_form(template, prompt, use_ai=True, auto_classify_hs=True)

    # Save if requested
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(filled, f, indent=2)
        print(f"Filled form saved to {output_path}")

    return filled


if __name__ == "__main__":
    # Example usage
    agent = TradeAgent()

    # Test product classification
    product = "Laptop computer with 15-inch display"
    suggestions = agent.get_hs_suggestions(product, top_n=3)
    print(f"\nHS Code suggestions for '{product}':")
    for s in suggestions:
        print(f"  {s['hs_code']} - {s['description'][:60]}... (confidence: {s['confidence']:.3f})")

    # Test form filling
    template = {
        "product_description": {"label": "Product Description", "type": "string"},
        "hs_code": {"label": "HS Code", "type": "string"},
        "quantity": {"label": "Quantity", "type": "string"}
    }

    prompt = "We are shipping 100 units of laptop computers"
    filled = agent.fill_trade_form(template, prompt, auto_classify_hs=True)
    print(f"\nFilled form:")
    print(json.dumps(filled, indent=2))
