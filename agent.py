"""LLM-powered form-filling agent.

Provides `fill_form(template: dict, prompt: str, db_data: Optional[dict]=None)` which
fills the form template fields from the user prompt using Groq LLM (Llama 3.3).

The template format is a JSON object with fields mapping to metadata, e.g.
{
  "name": {"label": "Full name", "type": "string"},
  "email": {"label": "Email address", "type": "string"}
}

The returned filled form is a dict mapping field names to values.
Requires GROQ_API_KEY environment variable.
"""
from typing import Dict, Any, Optional
import os
import re
import json

try:
    from groq import Groq
    groq_available = True
except Exception:
    Groq = None
    groq_available = False


def _call_openai_fill(template: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    """Call Groq LLM to extract values for template fields.

    Returns mapping field->value. Requires GROQ_API_KEY env var and the
    `groq` package.
    """
    if not groq_available:
        raise RuntimeError("groq package not installed. Run: pip install groq")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")
    client = Groq(api_key=api_key)

    # Build an instruction listing fields and labels.
    fields_list = []
    for k, meta in template.items():
        label = meta.get("label") or k
        fields_list.append(f"{k} ({label})")

    system = "You are an assistant that extracts form fields from a user's free-form text."
    user = (
        "Given the following form fields:\n"
        + "\n".join(fields_list)
        + "\n\nExtract values for each field in JSON where missing fields are empty strings.\n\n"
        + "User text:\n" + prompt
    )

    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # Log the LLM request
    print(f"\n{'='*80}")
    print(f"🧠 GROQ LLM REQUEST")
    print(f"{'='*80}")
    print(f"🤖 Model: {model}")
    print(f"\n📋 System Prompt:\n{'-'*80}\n{system}\n{'-'*80}")
    print(f"\n👤 User Prompt:\n{'-'*80}\n{user}\n{'-'*80}")

    # Use ChatCompletion with Groq SDK
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
            max_tokens=512,
            temperature=0,
        )
        text = resp.choices[0].message.content.strip()

        # Log the LLM response
        print(f"\n💬 RAW LLM RESPONSE:")
        print(f"{'-'*80}\n{text}\n{'-'*80}")

    except Exception as e:
        print(f"\n❌ Groq API Error: {e}")
        raise RuntimeError(f"Groq API request failed: {e}")

    # Try to find a JSON blob in the output
    m = re.search(r"\{(?:.|\n)*\}", text)
    if not m:
        # fallback: try to parse the whole text
        try:
            parsed = json.loads(text)
            print(f"\n✅ Parsed JSON (full text):")
        except Exception:
            print(f"\n❌ Failed to parse JSON from response")
            raise RuntimeError("Could not parse JSON from Groq response")
    else:
        parsed = json.loads(m.group(0))
        print(f"\n✅ Parsed JSON (extracted from text):")

    print(f"{'-'*80}\n{json.dumps(parsed, indent=2)}\n{'-'*80}")

    # Ensure all keys exist
    out = {}
    for k in template.keys():
        out[k] = parsed.get(k, "") if isinstance(parsed, dict) else ""

    print(f"\n✨ Extracted {sum(1 for v in out.values() if v)}/{len(out)} fields")
    print(f"{'='*80}\n")

    return out




def fill_form(template: Dict[str, Any], prompt: str, use_openai: bool = True, db_data: Optional[Dict[str, Any]] = None, auto_classify_hs: bool = False) -> Dict[str, Any]:
    """Fill the template from prompt using Groq LLM.

    Args:
        template: Form template dictionary
        prompt: User input text
        use_openai: Kept for backward compatibility, always uses LLM
        db_data: Optional database data for filling missing values
        auto_classify_hs: If True, automatically classify HS codes for products

    Returns:
        Dict mapping field names to extracted values

    Raises:
        RuntimeError: If Groq package not installed or API key not set
    """
    if not groq_available:
        raise RuntimeError("groq package not installed. Run: pip install groq")

    # Extract values using LLM
    result = _call_openai_fill(template, prompt)

    # Fill in missing values from db_data if available
    if db_data is not None:
        for key in template.keys():
            if not result.get(key) and key in db_data:
                result[key] = db_data[key]

    # Auto-classify HS codes if requested
    if auto_classify_hs:
        try:
            from llm_hs_classifier import get_classifier
            hs_classifier = get_classifier()

            # Look for product description fields
            product_desc = None
            for key in result.keys():
                if 'product' in key.lower() and 'desc' in key.lower():
                    product_desc = result.get(key)
                    break
                elif key.lower() in ['description', 'product_name', 'goods_description']:
                    product_desc = result.get(key)
                    break

            # If we found a product description, classify it
            if product_desc and product_desc.strip():
                print(f"\n🔍 Auto-classifying HS code for: {product_desc}")
                classification = hs_classifier.classify(product_desc, top_n=1)

                if classification.get('suggestions') and len(classification['suggestions']) > 0:
                    best_match = classification['suggestions'][0]
                    hs_code = best_match.get('hs_code', '')

                    # Find HS code field and populate it
                    for key in result.keys():
                        if 'hs' in key.lower() and 'code' in key.lower():
                            result[key] = hs_code
                            print(f"✅ Auto-filled HS code: {hs_code} (confidence: {best_match.get('confidence', 0):.2%})")
                            break
        except Exception as e:
            print(f"⚠️  HS code auto-classification failed: {e}")
            # Don't fail the entire form filling if HS classification fails

    return result


if __name__ == "__main__":
    # CLI for testing
    import argparse

    p = argparse.ArgumentParser(description="Fill forms using LLM")
    p.add_argument("--template", required=True, help="Path to template JSON file")
    p.add_argument("--prompt", required=True, help="User input text")
    args = p.parse_args()

    with open(args.template, "r") as f:
        tpl = json.load(f)

    out = fill_form(tpl, args.prompt)
    print(json.dumps(out, indent=2))
