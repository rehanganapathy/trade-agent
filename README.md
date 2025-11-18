# AI-Powered Trade Form Automation System 🚢

An intelligent agentic system that automates trade documentation with AI-powered form filling, automatic HS code classification, and vector database integration. Designed specifically for export/import businesses to eliminate tedious form-filling processes.

## 🎯 Overview

This system uses **Groq LLM** and **local embeddings** to:
- Automatically fill complex trade forms (Commercial Invoice, Bill of Lading, Customs Declaration, etc.)
- Classify products to HS codes using semantic similarity
- Learn from historical data using vector database
- Provide RESTful API for ERP integration

## ✨ Key Features

### 🤖 AI-Powered Form Filling
- **Groq LLM Integration**: Fast, accurate extraction using Llama models
- **Smart Heuristics**: Pattern matching for trade-specific fields (Incoterms, HS codes, currencies, ports, etc.)
- **Fallback System**: Automatically falls back to heuristics if AI is unavailable

### 📦 Automatic HS Code Classification
- **Semantic Search**: Uses sentence-transformers for local embedding generation
- **HTS Database**: Classify products against full Harmonized Tariff Schedule
- **Top-N Suggestions**: Get multiple HS code suggestions with confidence scores
- **Auto-fill**: Automatically fills HS code fields based on product descriptions

### 💾 Vector Database (ChromaDB)
- **Semantic Search**: Find similar past submissions
- **Autofill**: Learn from historical data to speed up form filling
- **Submission History**: Track and search through previous forms

### 📋 Comprehensive Trade Forms
- Commercial Invoice
- Packing List
- Bill of Lading
- Certificate of Origin
- Customs Declaration
- Proforma Invoice
- Customer Forms
- Employee Forms
- And more...

### 🌐 Modern Web Interface

**Two Frontend Options:**

1. **React Frontend (New!)** - Modern, optimized React application
   - Built with React 18, TypeScript, and TailwindCSS
   - Fast performance with Vite build tool
   - Beautiful, responsive design with smooth animations
   - Real-time form preview and AI status indicators
   - Dashboard with statistics and recent activity
   - Template management with visual editor
   - Submission history with powerful search
   - CRM dashboard for managing companies, leads, and products
   - Export to PDF, Excel, and JSON formats
   - See `frontend/README.md` for setup

2. **Classic Web UI** - Vanilla JavaScript interface
   - Three-tab UI: Fill Forms, Manage Templates, View History
   - Real-time field preview
   - Template management
   - HS code classification tool
   - Copy/download results
   - Mobile responsive

### 🔌 RESTful API
- `/api/fill` - Fill forms with optional HS classification
- `/api/classify-hs` - Classify products to HS codes
- `/api/templates` - Manage form templates
- `/api/history` - Search submission history

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API key (free at https://console.groq.com)

### Installation

```bash
# Clone or navigate to the repository
cd /path/to/trade/db

# Create and activate virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template and configure
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### Configuration

Create a `.env` file with:

```bash
# Required: Get your free API key from https://console.groq.com
GROQ_API_KEY=gsk_your-groq-api-key-here

# Optional configurations
GROQ_MODEL=llama-3.3-70b-versatile  # or llama-3.1-70b-versatile
CHROMA_PERSIST_DIR=./chroma_db
HTS_JSON_PATH=hts_current.json  # Path to HTS data file
```

### Run the Application

**Option 1: Backend Only (Classic UI)**

```bash
python web_app.py
```

Then open http://127.0.0.1:5000 in your browser.

**Option 2: Backend + React Frontend (Recommended)**

Terminal 1 - Start Backend:
```bash
python web_app.py
```

Terminal 2 - Start React Frontend:
```bash
cd frontend
npm install  # First time only
npm run dev
```

Then open http://localhost:3000 in your browser.

## 📖 Usage Examples

### Web Interface

1. **Fill a Trade Form**
   - Select template (e.g., "commercial_invoice.json")
   - Paste trade details or use example prompts from `examples/`
   - Toggle "Use AI Extraction" for Groq LLM processing
   - Enable "Auto-classify HS codes" for automatic product classification
   - Click "Fill Form"

2. **Classify HS Codes**
   - Enter product description
   - Get top 5 HS code suggestions with confidence scores

3. **View History**
   - Search past submissions
   - Filter by template type

### CLI Usage

```bash
# Basic form filling with heuristics
python run_agent.py \
  --template templates/commercial_invoice.json \
  --prompt-file examples/commercial_invoice_prompt.txt \
  --out filled_invoice.json

# With Groq AI extraction
python run_agent.py \
  --template templates/bill_of_lading.json \
  --prompt "B/L #123, vessel MAERSK ATLANTA, from Oakland to Felixstowe..." \
  --openai \
  --out filled_bl.json

# Using the trade agent with HS classification
python trade_agent.py
```

### API Integration

```python
import requests

# Fill a commercial invoice
response = requests.post('http://localhost:5000/api/fill', json={
    'template': 'commercial_invoice.json',
    'prompt': '''
        Invoice CI-2025-001234 dated 2025-11-15
        From TechExport Solutions, San Francisco to GlobalTech Ltd, London
        500 units of Wireless Headphones at $89.99 USD
        Incoterms: CIF London
        Gross weight: 250 kg
    ''',
    'use_openai': True,
    'auto_classify_hs': True,  # Automatically classify HS codes
    'save_to_db': True
})

filled_form = response.json()['filled']
print(filled_form)

# Classify a product to HS code
response = requests.post('http://localhost:5000/api/classify-hs', json={
    'product_description': 'Premium wireless bluetooth headphones with noise cancellation',
    'top_n': 5
})

suggestions = response.json()['suggestions']
for suggestion in suggestions:
    print(f"{suggestion['hs_code']}: {suggestion['description']} ({suggestion['confidence']:.2%})")
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Frontend                         │
│              (HTML/CSS/JS - Modern UI)                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   Flask API                             │
│                  (web_app.py)                           │
└───┬──────────────┬──────────────┬──────────────────────┘
    │              │              │
    ▼              ▼              ▼
┌─────────┐  ┌──────────┐  ┌──────────────┐
│ Agent   │  │  Trade   │  │  Vector DB   │
│ (Groq)  │  │  Agent   │  │  (ChromaDB)  │
└─────────┘  └────┬─────┘  └──────────────┘
                  │
                  ▼
            ┌──────────────┐
            │ HS Classifier│
            │ (Embeddings) │
            └──────────────┘
```

## 📝 Trade-Specific Features

### Supported Incoterms
EXW, FCA, CPT, CIP, DAP, DPU, DDP, FAS, FOB, CFR, CIF

### Currency Recognition
USD, EUR, GBP, JPY, CNY, INR, AUD, CAD, CHF, SGD

### Smart Field Extraction
- HS Codes (6-10 digits)
- Container Numbers (ISO format)
- Invoice/BL Numbers
- Port Names
- Country Names
- Weights and Dimensions
- Tax IDs
- Email and Phone Numbers
- Dates (ISO format)

## 📦 HTS Data Setup (Optional)

For HS code classification, you need the HTS database:

1. Download from [USITC](https://hts.usitc.gov/)
2. Place `hts_current.json` in project root
3. On first run, the system will generate embeddings (cached for future use)

Note: The system works without HTS data, but HS code classification will be unavailable.

## 🔧 Configuration Options

### Agent Modes

1. **Heuristic Mode** (No API key needed)
   - Fast pattern-matching extraction
   - Works offline
   - Good for structured data

2. **AI Mode** (Requires Groq API key)
   - More accurate extraction
   - Handles unstructured text
   - Better context understanding

3. **Hybrid Mode** (Recommended)
   - Tries AI first, falls back to heuristics
   - Best of both worlds

### Vector DB Options

Enable autofill from historical data:
```python
# In API calls
{
    "use_db": true,      # Use vector DB for autofill
    "save_to_db": true   # Save this submission for future use
}
```

## 🧪 Testing

```bash
# Test basic form filling
python run_agent.py --template templates/example_form.json \
  --prompt-file examples/sample_prompt.txt

# Test trade agent
python trade_agent.py

# Test HS classification
python -c "
from trade_agent import TradeAgent
agent = TradeAgent()
results = agent.get_hs_suggestions('laptop computer', top_n=3)
for r in results: print(r)
"

# Test web app
python web_app.py
# Visit http://127.0.0.1:5000 and try filling forms
```

## 📚 Available Templates

- `commercial_invoice.json` - International sales invoice
- `packing_list.json` - Shipment packing details
- `bill_of_lading.json` - Ocean freight documentation
- `certificate_of_origin.json` - Origin certification
- `customs_declaration.json` - Import/export customs forms
- `proforma_invoice.json` - Pre-shipment invoice
- `trade_form.json` - General trade information
- `customer_form.json` - Customer information
- `example_form.json` - Employee/general forms

## 🛠️ Development

### Project Structure
```
.
├── agent.py                    # Core form-filling with Groq
├── trade_agent.py             # Trade agent with HS classification
├── vector_db.py               # ChromaDB integration
├── web_app.py                 # Flask application
├── main.py                    # HS classification entry point
├── config.py                  # Configuration
├── embedding_generator.py     # Embedding generation
├── requirements.txt           # Python dependencies
├── templates/                 # Form templates (JSON)
│   ├── commercial_invoice.json
│   ├── packing_list.json
│   └── ...
├── examples/                  # Example prompts
│   ├── commercial_invoice_prompt.txt
│   └── ...
├── data_collection/
│   ├── data_loader.py        # HTS data loader
│   └── classifier.py         # HS code classifier
└── web/
    ├── templates/
    │   └── index.html        # Frontend UI
    └── static/
        ├── style.css         # Styles
        └── app.js            # Frontend logic
```

### Adding Custom Fields

1. **Edit Template**
   ```json
   {
     "custom_field": {
       "label": "Custom Field Label",
       "type": "string"
     }
   }
   ```

2. **Add Heuristics** (optional, in `agent.py`):
   ```python
   if 'custom_field' in key.lower():
       # Add extraction pattern
       match = re.search(r'pattern', prompt)
       if match:
           out[key] = match.group(1)
   ```

## 🚀 Deployment

### Production Setup

```bash
# Use a production WSGI server
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app

# Or use Docker (create Dockerfile)
```

### Environment Variables

```bash
export GROQ_API_KEY=gsk_your_key
export GROQ_MODEL=llama-3.3-70b-versatile
export FLASK_ENV=production
```

## 🔒 Security Notes

- Never commit API keys to version control
- Use environment variables for sensitive data
- Implement authentication for production APIs
- Sanitize user inputs
- Use HTTPS in production

## 🐛 Troubleshooting

### Common Issues

**Groq API errors**
```bash
# Check API key is set
echo $GROQ_API_KEY

# Test API connection
python -c "from groq import Groq; print(Groq(api_key='your_key').models.list())"
```

**Vector DB not available**
```bash
pip install chromadb
```

**HTS data not found**
- System will work without HTS data
- HS classification feature will be unavailable
- Download from USITC if needed

**Import errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## 📈 Roadmap

- [ ] PDF form population
- [ ] Multi-language support
- [ ] Validation rules engine
- [ ] Approval workflows
- [ ] Document scanning/OCR integration
- [ ] Multi-step form wizards
- [ ] Analytics dashboard
- [ ] Webhook notifications
- [ ] Multi-tenancy support

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional trade form templates
- More extraction heuristics
- Better HS code classification
- UI/UX enhancements
- Documentation improvements

## 📄 License

MIT License - Free to use in your projects!

## 🙏 Credits

- **Groq**: Fast LLM inference
- **Sentence Transformers**: Local embeddings
- **ChromaDB**: Vector database
- **Flask**: Web framework

## 📞 Support

For issues, questions, or contributions:
- Create an issue in the repository
- Check existing documentation
- Review example files in `examples/`

---

**Built for automating international trade documentation** 🌍📦
