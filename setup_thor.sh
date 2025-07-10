EVEN SIMPLER - One Command Setup
Let me create a setup script that handles everything:
bashCopy# setup_thor.sh
#!/bin/bash
set -e

echo "🔨 Setting up THOR AI Assistant..."

# Check Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python not found!"
    echo "Please install Python 3.8+ first:"
    echo "  - Windows: https://python.org/downloads/"
    echo "  - Mac: brew install python3"
    echo "  - Linux: sudo apt install python3 python3-pip"
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    PIP_CMD=pip3
else
    PYTHON_CMD=python
    PIP_CMD=pip
fi

echo "✅ Found Python: $($PYTHON_CMD --version)"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found. Are you in the thor directory?"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
$PYTHON_CMD -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo "⬆️ Upgrading pip..."
$PIP_CMD install --upgrade pip

# Install requirements
echo "📥 Installing requirements..."
$PIP_CMD install -r requirements.txt

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  API key not set!"
    echo "Please set your Anthropic API key:"
    echo "  export ANTHROPIC_API_KEY='your_key_here'"
    echo ""
    echo "Get a key at: https://console.anthropic.com/"
    echo ""
    echo "After setting the key, run:"
    echo "  source venv/bin/activate"
    echo "  python src/thor_main.py"
else
    echo "✅ API key found"
    echo "🎉 Setup complete!"
    echo ""
    echo "To run THOR:"
    echo "  python src/thor_main.py"
fi
Fixed thor_main.py (Based on Current Repo)
