#!/bin/bash
# Setup script for AI Form Filler Agent

echo "🤖 AI Form Filler Agent - Setup"
echo "================================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
echo "✓ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. (Optional) Set your OpenAI API key:"
echo "   export OPENAI_API_KEY='sk-...'"
echo ""
echo "2. Start the web application:"
echo "   python web_app.py"
echo ""
echo "3. Open your browser to:"
echo "   http://127.0.0.1:5000"
echo ""
echo "For CLI usage:"
echo "   python run_agent.py --template templates/example_form.json --prompt-file examples/sample_prompt.txt"
echo ""
