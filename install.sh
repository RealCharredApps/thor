#!/bin/bash
# install.sh - CORRECTED VERSION

echo "🚀 Installing THOR Advanced AI Development Assistant..."

# Get the current directory
THOR_DIR=$(pwd)

# Create virtual environment if it doesn't exist
if [ ! -d "thor_env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv thor_env
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source thor_env/bin/activate

# Upgrade pip
echo "📈 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Install THOR in development mode
echo "🛠️  Installing THOR..."
pip install -e .

echo "⚙️  Setting up configuration..."
python3 -c "
import sys
import os
sys.path.insert(0, 'src')
try:
    from core.config import ConfigManager
    config = ConfigManager()
    config.save_config()
    print('✅ Configuration created')
except Exception as e:
    print(f'❌ Configuration error: {e}')
"

echo "🖥️  Creating macOS shortcut..."
python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from macos.thor_app import create_thor_app
    create_thor_app()
except Exception as e:
    print(f'⚠️  Could not create macOS app: {e}')
"

echo ""
echo "✅ THOR installation complete!"
echo ""
echo "🔧 SETUP INSTRUCTIONS:"
echo "1. Set your API key: export ANTHROPIC_API_KEY='your_key_here'"
echo "2. Optional: Set Argus path: export ARGUS_PATH='/path/to/argus'"
echo "3. Run THOR: thor"
echo ""
echo "📁 Project directory: $THOR_DIR"
echo "🐍 Virtual environment: thor_env"
echo "🚀 Command: thor"