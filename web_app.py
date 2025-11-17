"""Browser-friendly Flask wrapper for the form-filling agent."""
from pathlib import Path
from typing import List
import json
import os

from flask import Flask, jsonify, render_template, request

from agent import fill_form
from vector_db import VectorDB, get_autofill_data

# Import the new LLM-based HS classifier
try:
    from llm_hs_classifier import get_classifier
    hs_classifier = get_classifier()
    hs_classifier_available = True
    print("✅ LLM HS Classifier initialized successfully!")
except Exception as e:
    print(f"⚠️  LLM HS Classifier not available: {e}")
    hs_classifier = None
    hs_classifier_available = False

# Try to import trade agent (optional, requires sentence-transformers)
try:
    from trade_agent import TradeAgent
    trade_agent_available = True
except Exception as e:
    print(f"Trade agent not available: {e}")
    TradeAgent = None
    trade_agent_available = False


BASE_DIR = Path(__file__).parent
TEMPLATE_ROOT = BASE_DIR / "templates"
WEB_ROOT = BASE_DIR / "web"

app = Flask(
    __name__,
    template_folder=str(WEB_ROOT / "templates"),
    static_folder=str(WEB_ROOT / "static"),
    static_url_path="/static",

)

# Initialize vector DB
try:
    vector_db = VectorDB()
except Exception as e:
    print(f"Warning: Vector DB not available: {e}")
    vector_db = None

# Initialize trade agent (only if available)
trade_agent = None
if trade_agent_available:
    try:
        trade_agent = TradeAgent()
        print("Trade agent initialized successfully!")
    except Exception as e:
        print(f"Warning: Trade agent initialization failed: {e}")
        trade_agent = None
else:
    print("Trade agent disabled (sentence-transformers not installed)")


def _list_form_templates() -> List[str]:
    if not TEMPLATE_ROOT.exists():
        return []
    return [p.name for p in TEMPLATE_ROOT.glob("*.json")]


@app.route("/")
def index():
    template_files = _list_form_templates()
    db_available = vector_db is not None
    return render_template("index.html", templates=template_files, db_available=db_available)


@app.route("/api/fill", methods=["POST"])
def api_fill():
    data = request.get_json(force=True)
    template_name = data.get("template")
    prompt = data.get("prompt", "")
    use_db = bool(data.get("use_db", True))
    save_to_db = bool(data.get("save_to_db", False))
    auto_classify_hs = bool(data.get("auto_classify_hs", True))

    print("\n" + "="*80)
    print("🤖 NEW FORM FILL REQUEST")
    print("="*80)
    print(f"📋 Template: {template_name}")
    print(
        f"🔧 Use DB: {use_db} | Save to DB: {save_to_db} | Auto-classify HS: {auto_classify_hs}")
    print(f"\n📝 User Prompt:\n{'-'*80}\n{prompt}\n{'-'*80}")

    if not template_name:
        return jsonify({"error": "template is required"}), 400
    template_path = TEMPLATE_ROOT / template_name
    if not template_path.exists():
        return jsonify({"error": f"template {template_name} not found"}), 404

    template_json = json.loads(template_path.read_text())
    print(f"\n📄 Template Fields: {list(template_json.keys())}")

    # Get autofill data from vector DB if enabled
    db_data = None
    if use_db and vector_db:
        db_data = get_autofill_data(prompt, template_name, vector_db)
        if db_data:
            print(f"\n💾 Vector DB Data Retrieved: {len(db_data)} fields")

    # Use LLM extraction to fill the form
    print(f"\n🚀 Starting LLM extraction...")
    filled = fill_form(template_json, prompt, use_openai=True, db_data=db_data)

    # Apply intelligent HS code classification if enabled
    if auto_classify_hs and hs_classifier_available and hs_classifier:
        print(f"\n🔍 Attempting HS code classification...")
        # Look for product description in filled form
        product_desc = None
        for key in ['product_description', 'description', 'description_of_goods', 'product_name', 'product']:
            if key in filled and filled[key]:
                product_desc = filled[key]
                print(f"   Found product description in field '{key}': {product_desc}")
                break

        if product_desc:
            # Classify using LLM
            hs_results = hs_classifier.classify(product_desc, top_n=1)
            if hs_results and hs_results[0]:
                best_match = hs_results[0]
                hs_code = best_match['hs_code']

                # Find HS code field in template and fill it
                for key in ['hs_code', 'hts_code', 'harmonized_code', 'tariff_code']:
                    if key in template_json:
                        filled[key] = hs_code
                        print(f"   ✅ Filled HS code field '{key}' with: {hs_code}")
                        print(f"   Confidence: {best_match['confidence']:.1%}")
                        print(f"   Reasoning: {best_match['reasoning']}")
                        break
        else:
            print(f"   ⚠️  No product description found for HS classification")

    print(f"\n✅ LLM Extraction Complete!")
    print(
        f"📊 Filled Fields: {sum(1 for v in filled.values() if v)}/{len(filled)}")
    print(f"\n🎯 Final Result:")
    print(json.dumps(filled, indent=2))
    print("="*80 + "\n")

    # Save to vector DB if requested
    if save_to_db and vector_db:
        try:
            vector_db.add_submission(filled, template_name)
            print(f"💾 Saved to Vector DB successfully!")
        except Exception as e:
            print(f"❌ Error saving to DB: {e}")

    return jsonify({"filled": filled, "from_db": bool(db_data)})


@app.route("/api/templates", methods=["GET"])
def api_list_templates():
    """List all available templates."""
    template_files = _list_form_templates()
    templates = []
    for name in template_files:
        template_path = TEMPLATE_ROOT / name
        template_json = json.loads(template_path.read_text())
        templates.append({
            "name": name,
            "fields": list(template_json.keys())
        })
    return jsonify({"templates": templates})


@app.route("/api/templates/<template_name>", methods=["GET"])
def api_get_template(template_name):
    """Get a specific template."""
    template_path = TEMPLATE_ROOT / template_name
    if not template_path.exists():
        return jsonify({"error": f"template {template_name} not found"}), 404
    template_json = json.loads(template_path.read_text())
    return jsonify({"template": template_json})


@app.route("/api/templates", methods=["POST"])
def api_create_template():
    """Create a new template."""
    data = request.get_json(force=True)
    name = data.get("name")
    template = data.get("template")

    if not name or not template:
        return jsonify({"error": "name and template are required"}), 400

    if not name.endswith(".json"):
        name = f"{name}.json"

    template_path = TEMPLATE_ROOT / name
    if template_path.exists():
        return jsonify({"error": f"template {name} already exists"}), 400

    template_path.write_text(json.dumps(template, indent=2))
    return jsonify({"success": True, "name": name})


@app.route("/api/history", methods=["GET"])
def api_get_history():
    """Get submission history."""
    if not vector_db:
        return jsonify({"error": "Vector DB not available"}), 503

    query = request.args.get("query", "")
    template = request.args.get("template")
    limit = int(request.args.get("limit", 10))

    results = vector_db.search_similar(query, template, top_k=limit)
    return jsonify({"history": results})


@app.route("/api/classify-hs", methods=["POST"])
def api_classify_hs():
    """Classify a product to HS codes using intelligent LLM classifier."""
    if not hs_classifier_available or not hs_classifier:
        return jsonify({"error": "HS classifier not available"}), 503

    data = request.get_json(force=True)
    product_description = data.get("product_description", "")
    top_n = int(data.get("top_n", 5))

    if not product_description:
        return jsonify({"error": "product_description is required"}), 400

    print(f"\n🔍 API HS Classification Request")
    print(f"📝 Product: {product_description}")
    print(f"🎯 Top N: {top_n}")

    suggestions = hs_classifier.classify(product_description, top_n=top_n)

    return jsonify({"suggestions": suggestions})


if __name__ == "__main__":
    app.run(debug=True)
