# 🚀 Getting Started - Trade Form Automation

## Quick Start (5 minutes)

### Step 1: Set Up Groq API (Required for AI features)

1. Visit https://console.groq.com
2. Sign up for free account
3. Generate API key
4. Create `.env` file:

```bash
cd /Users/rehanganapathy/Desktop/Trade/db
echo "GROQ_API_KEY=gsk_your_actual_key_here" > .env
echo "GROQ_MODEL=llama-3.3-70b-versatile" >> .env
```

### Step 2: Test the System

```bash
# Activate virtual environment
source .venv/bin/activate

# Test with heuristics (no API key needed)
python3 run_agent.py \
  --template templates/commercial_invoice.json \
  --prompt-file examples/commercial_invoice_prompt.txt \
  --out result.json

# View results
cat result.json
```

### Step 3: Start Web Application

```bash
python3 web_app.py
```

Then open http://127.0.0.1:5000 in your browser!

## 📝 Try These Examples

### Example 1: Commercial Invoice

```bash
python3 run_agent.py \
  --template templates/commercial_invoice.json \
  --prompt "Invoice CI-2025-12345 dated 2025-11-20.
From TechExport Inc, San Francisco, USA.
To GlobalTrade Ltd, London, UK.
Product: 1000 units of Bluetooth Headphones at $49.99 USD.
Incoterms: FOB San Francisco.
Gross weight: 500 kg. Country of origin: China" \
  --out commercial_invoice_filled.json
```

### Example 2: Bill of Lading

```bash
python3 run_agent.py \
  --template templates/bill_of_lading.json \
  --prompt-file examples/bill_of_lading_prompt.txt \
  --out bl_filled.json
```

### Example 3: With AI Extraction (needs API key)

```bash
python3 run_agent.py \
  --template templates/customs_declaration.json \
  --prompt-file examples/customs_declaration_prompt.txt \
  --openai \
  --out customs_filled.json
```

## 🌐 Web Interface Usage

1. **Fill Form Tab**
   - Select template (e.g., commercial_invoice.json)
   - Enter/paste trade details
   - Toggle "Use AI Extraction" (requires Groq API key)
   - Click "Fill Form"

2. **Templates Tab**
   - View all available templates
   - Create custom templates
   - See field definitions

3. **History Tab**
   - Search past submissions
   - Filter by template type

## 🎯 Available Form Templates

1. **commercial_invoice.json** - International sales
2. **packing_list.json** - Shipment details
3. **bill_of_lading.json** - Freight documentation
4. **certificate_of_origin.json** - Origin certification
5. **customs_declaration.json** - Import/export customs
6. **proforma_invoice.json** - Pre-shipment invoice
7. **customer_form.json** - Customer information
8. **example_form.json** - General forms

## 🔌 API Examples

### Fill a Form
```python
import requests

response = requests.post('http://localhost:5000/api/fill', json={
    'template': 'commercial_invoice.json',
    'prompt': 'Your trade details here...',
    'use_openai': True,  # Set to False to use heuristics only
    'save_to_db': True
})

filled_form = response.json()['filled']
print(filled_form)
```

### Classify HS Code (requires torch/sentence-transformers)
```python
response = requests.post('http://localhost:5000/api/classify-hs', json={
    'product_description': 'Wireless bluetooth headphones',
    'top_n': 5
})

suggestions = response.json()['suggestions']
for s in suggestions:
    print(f"{s['hs_code']}: {s['confidence']:.2%}")
```

## ⚙️ Configuration Options

### Environment Variables (.env file)

```bash
# Required for AI features
GROQ_API_KEY=gsk_your_key_here

# Optional
GROQ_MODEL=llama-3.3-70b-versatile  # or llama-3.1-70b-versatile
CHROMA_PERSIST_DIR=./chroma_db
HTS_JSON_PATH=hts_current.json
```

## 🔧 Optional: Install HS Code Classification

For automatic HS code classification:

```bash
# In your virtual environment
pip install torch sentence-transformers

# Download HTS data from https://hts.usitc.gov/
# Place hts_current.json in project root
```

## 📊 System Modes

### 1. Heuristic Mode (Default, No API Key Needed)
- Fast pattern matching
- Works offline
- Good for structured data

### 2. AI Mode (Requires Groq API Key)
- LLM-powered extraction
- Better for unstructured text
- More accurate

### 3. Hybrid Mode (Recommended)
- Tries AI first, falls back to heuristics
- Best reliability

## 🎓 Smart Field Extraction

The system automatically recognizes:

- **Incoterms**: FOB, CIF, EXW, DDP, etc.
- **Currencies**: USD, EUR, GBP, JPY, etc.
- **HS Codes**: 6-10 digit codes
- **Ports**: Port of loading/discharge
- **Countries**: Origin/destination
- **Weights**: kg, tons
- **Dimensions**: L×W×H in cm
- **Container Numbers**: ISO format
- **Emails & Phones**
- **Dates**: ISO format (YYYY-MM-DD)

## 🐛 Troubleshooting

### "GROQ_API_KEY not set" Error
```bash
# Make sure .env file exists
cat .env

# Should show:
# GROQ_API_KEY=gsk_your_key_here
```

### Web app not starting
```bash
# Check if port 5000 is free
lsof -ti:5000

# Kill existing process if needed
lsof -ti:5000 | xargs kill -9
```

### Import errors
```bash
# Reinstall dependencies
source .venv/bin/activate
pip install -r requirements.txt
```

## 📈 Next Steps

1. **✅ Basic Setup** (Completed above)
2. **Customize Templates**: Edit JSON files in `templates/`
3. **Add Custom Heuristics**: Edit `agent.py`
4. **Integrate with ERP**: Use REST API
5. **Deploy to Production**: Use gunicorn or Docker

## 🎯 Real-World Workflow

```bash
# 1. Receive trade details from customer/email
# 2. Paste into web interface or call API
# 3. Get filled form in seconds
# 4. Review and export
# 5. System learns from your data (vector DB)
```

## 💡 Pro Tips

1. **Save to Database**: Enable "Save to DB" to learn from your submissions
2. **Use Examples**: Check `examples/` folder for realistic prompts
3. **Combine Forms**: Use multiple templates for complete documentation
4. **Batch Processing**: Use API for high-volume processing
5. **Custom Templates**: Create your own for specific needs

## 📞 Need Help?

- Check `README.md` for comprehensive documentation
- Review `IMPLEMENTATION_SUMMARY.md` for technical details
- See `examples/` for sample prompts
- Test with `run_agent.py` for CLI usage

## 🎉 You're Ready!

Start automating your trade documentation now:

```bash
# Start the web app
python3 web_app.py

# Or use CLI
python3 run_agent.py --template templates/commercial_invoice.json \
  --prompt "Your trade details..."
```

**Happy Trading! 🚢📦🌍**

