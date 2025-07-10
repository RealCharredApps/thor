# install.sh
#!/bin/bash

echo "🚀 Installing THOR Advanced AI Development Assistant..."

# Create virtual environment
python3 -m venv thor_env
source thor_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Create configuration
echo "⚙️  Setting up configuration..."
python -c "
from src.core.config import ConfigManager
config = ConfigManager()
config.save_config()
print('✅ Configuration created')
"

# Create macOS shortcut
echo "🖥️  Creating macOS shortcut..."
python src/macos/thor_shortcut.py

echo "✅ THOR installation complete!"
echo "🔧 Don't forget to set your ANTHROPIC_API_KEY in your environment"
echo "🚀 Run 'thor' to start the interactive session"