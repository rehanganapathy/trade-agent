"""LLM-based HTS/HS Code Classification System.

Uses Groq LLM to intelligently classify product descriptions to HS codes.
This approach requires no additional dependencies beyond Groq.
"""

import json
import os
from typing import List, Dict, Tuple
from groq import Groq


class LLMHSClassifier:
    """Intelligent HS code classifier using LLM reasoning."""

    def __init__(self, hts_data_path: str = "hts_current.json"):
        """Initialize the LLM-based HS classifier.

        Args:
            hts_data_path: Path to HTS JSON database
        """
        self.hts_data_path = hts_data_path
        self.hs_database = self._load_hts_database()
        self.groq_client = None

        # Initialize Groq client
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            self.groq_client = Groq(api_key=api_key)

        print(f"✅ LLM HS Classifier initialized with {len(self.hs_database)} HS codes")

    def _load_hts_database(self) -> List[Dict]:
        """Load the HTS database from JSON file."""
        try:
            with open(self.hts_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"📦 Loaded {len(data)} HTS entries from {self.hts_data_path}")
            return data
        except FileNotFoundError:
            print(f"⚠️  HTS database not found at {self.hts_data_path}")
            return []
        except Exception as e:
            print(f"❌ Error loading HTS database: {e}")
            return []

    def classify(
        self,
        product_description: str,
        top_n: int = 5,
        temperature: float = 0.1
    ) -> List[Dict[str, any]]:
        """Classify a product description to HS codes using LLM.

        Args:
            product_description: Description of the product to classify
            top_n: Number of top matches to return
            temperature: LLM temperature (lower = more deterministic)

        Returns:
            List of dicts with keys: hs_code, description, confidence, reasoning
        """
        if not self.hs_database:
            print("❌ No HTS database loaded")
            return []

        if not self.groq_client:
            print("❌ Groq client not initialized")
            return []

        if not product_description or not product_description.strip():
            return []

        print(f"\n{'='*80}")
        print(f"🔍 HS CODE CLASSIFICATION")
        print(f"{'='*80}")
        print(f"📝 Product: {product_description}")
        print(f"🎯 Requesting top {top_n} matches...")

        # Create a knowledge base of HS codes for the LLM
        # Sample a diverse subset to stay within token limits
        sampled_hs = self._create_knowledge_sample()

        # Build the LLM prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(product_description, sampled_hs, top_n)

        try:
            # Call Groq LLM
            response = self.groq_client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=1000
            )

            raw_response = response.choices[0].message.content.strip()
            print(f"\n💬 LLM Response:\n{'-'*80}\n{raw_response}\n{'-'*80}")

            # Parse the LLM response
            results = self._parse_llm_response(raw_response, top_n)

            print(f"\n✅ Found {len(results)} HS code matches")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['hs_code']}: {result['description'][:60]}... ({result['confidence']:.1%})")

            print(f"{'='*80}\n")

            return results

        except Exception as e:
            print(f"❌ Error during LLM classification: {e}")
            return []

    def _create_knowledge_sample(self) -> List[Dict]:
        """Create a diverse sample of the HS database for the LLM.

        Samples entries to provide good coverage while staying within token limits.
        """
        # For now, include all entries if under 120 items
        # In production, you might want to implement smart sampling
        if len(self.hs_database) <= 120:
            return self.hs_database

        # Sample evenly across the database
        step = len(self.hs_database) // 120
        return [self.hs_database[i] for i in range(0, len(self.hs_database), step)]

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the LLM."""
        return """You are an expert in international trade and HS (Harmonized System) code classification.
Your role is to accurately classify products to their correct HS codes based on product descriptions.

HS codes are standardized numerical codes used worldwide to classify traded products.
Each code corresponds to a specific product category.

Your task is to:
1. Analyze the product description carefully
2. Match it to the most appropriate HS codes from the provided database
3. Provide confidence scores and reasoning for each match
4. Return results in the exact JSON format specified"""

    def _build_user_prompt(self, product_desc: str, hs_sample: List[Dict], top_n: int) -> str:
        """Build the user prompt with product and HS database."""
        # Format the HS database for the prompt
        hs_list = "\n".join([
            f"{item['htsno']}: {item['description']}"
            for item in hs_sample
        ])

        prompt = f"""Product Description to Classify:
"{product_desc}"

Available HS Codes Database:
{hs_list}

Task: Classify the product to the top {top_n} most appropriate HS codes.

Return your response in this EXACT JSON format:
{{
  "matches": [
    {{
      "hs_code": "8518300000",
      "confidence": 0.95,
      "reasoning": "Brief explanation of why this code matches"
    }}
  ]
}}

Consider:
- Product material, function, and intended use
- Industry standards for similar products
- The hierarchy and specificity of HS codes

Return ONLY the JSON, no additional text."""

        return prompt

    def _parse_llm_response(self, response_text: str, top_n: int) -> List[Dict]:
        """Parse the LLM's JSON response into structured results."""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_json = json.loads(json_match.group(0))
            else:
                response_json = json.loads(response_text)

            matches = response_json.get("matches", [])

            # Enrich with full descriptions from database
            results = []
            for match in matches[:top_n]:
                hs_code = match.get("hs_code", "")
                confidence = match.get("confidence", 0.5)
                reasoning = match.get("reasoning", "")

                # Find full description from database
                full_desc = ""
                for item in self.hs_database:
                    if item["htsno"] == hs_code:
                        full_desc = item["description"]
                        break

                results.append({
                    "hs_code": hs_code,
                    "description": full_desc or "Description not found",
                    "confidence": float(confidence),
                    "reasoning": reasoning
                })

            return results

        except Exception as e:
            print(f"⚠️  Error parsing LLM response: {e}")
            # Fallback: try simple keyword matching
            return self._fallback_keyword_match(response_text, top_n)

    def _fallback_keyword_match(self, product_desc: str, top_n: int) -> List[Dict]:
        """Fallback: Simple keyword-based matching if LLM response fails."""
        print("⚠️  Using fallback keyword matching")

        product_words = set(product_desc.lower().split())
        scored_entries = []

        for entry in self.hs_database:
            desc_words = set(entry["description"].lower().split())
            # Simple word overlap score
            overlap = len(product_words & desc_words)
            if overlap > 0:
                scored_entries.append((entry, overlap))

        # Sort by score
        scored_entries.sort(key=lambda x: x[1], reverse=True)

        # Return top N
        results = []
        for entry, score in scored_entries[:top_n]:
            results.append({
                "hs_code": entry["htsno"],
                "description": entry["description"],
                "confidence": min(0.5, score * 0.1),  # Cap at 50% for keyword matching
                "reasoning": "Keyword-based match (fallback)"
            })

        return results

    def get_hs_suggestions(self, product_description: str, top_n: int = 5) -> List[Dict]:
        """Alias for classify() to match existing API."""
        return self.classify(product_description, top_n)


# Singleton instance
_classifier_instance = None


def get_classifier() -> LLMHSClassifier:
    """Get or create the singleton classifier instance."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = LLMHSClassifier()
    return _classifier_instance


if __name__ == "__main__":
    # Test the classifier
    classifier = LLMHSClassifier()

    test_products = [
        "Wireless Bluetooth headphones with noise cancellation",
        "Cotton t-shirts for men",
        "Laptop computer with 15 inch screen",
        "Fresh mozzarella cheese",
        "LED television 55 inch"
    ]

    for product in test_products:
        print(f"\n\nTesting: {product}")
        print("=" * 80)
        results = classifier.classify(product, top_n=3)

        if results:
            for i, result in enumerate(results, 1):
                print(f"\n{i}. HS Code: {result['hs_code']}")
                print(f"   Description: {result['description']}")
                print(f"   Confidence: {result['confidence']:.1%}")
                print(f"   Reasoning: {result['reasoning']}")
        else:
            print("No results found")
