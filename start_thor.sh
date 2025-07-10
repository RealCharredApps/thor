#!/bin/bash
# thor/start_thor.sh

echo "🔨 Starting THOR AI Development Assistant"
echo "========================================"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Check if API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not set"
    echo "Please set your API key:"
    echo "export ANTHROPIC_API_KEY='your_api_key_here'"
    exit 1
fi

# Check Python version
python_version=$(python --version 2>&1)
echo "🐍 Python version: $python_version"

# Install dependencies if needed
if [ ! -f "requirements_installed.flag" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    touch requirements_installed.flag
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p thor/logs thor/memory thor/artifacts

# Run tests
echo "🧪 Running tests..."
python test_thor.py

# Check if tests passed
if [ $? -eq 0 ]; then
    echo "✅ Tests passed! Starting THOR..."
    python src/thor_main.py --interactive
else
    echo "❌ Tests failed. Check configuration."
    exit 1
fi