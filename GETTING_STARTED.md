# thor/docs/GETTING_STARTED.md

# 🚀 Getting Started with THOR

## Quick Setup (5 minutes)

### 1. Clone and Install
```bash
git clone https://github.com/RealCharredApps/thor.git
cd thor
2. Set API Key
bashCopyexport ANTHROPIC_API_KEY="your_api_key_here"
3. Install Dependencies
bashCopypip install -r requirements.txt
pip install -e .
4. Test Installation
bashCopypython test_thor.py
5. Start THOR
bashCopythor --interactive
Detailed Setup
Prerequisites

Python 3.8 or higher
pip package manager
Anthropic API key (Get one here)

Installation Options
Option 1: Quick Setup (Recommended)
bashCopymake setup
Option 2: Manual Setup
bashCopy# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Create directories
mkdir -p thor/logs thor/memory thor/artifacts
Option 3: Docker Setup
bashCopydocker build -t thor .
docker run -e ANTHROPIC_API_KEY="your_key" -it thor
Configuration
Environment Variables
bashCopy# Required
export ANTHROPIC_API_KEY="your_api_key_here"

# Optional
export THOR_LOG_LEVEL="INFO"
export THOR_ENABLE_SWARM="true"
export THOR_MONTHLY_BUDGET="5.0"
Configuration File
Edit config/thor_config.yaml:
yamlCopyanthropic_api_key: "${ANTHROPIC_API_KEY}"
default_model: "claude-3-5-sonnet-20241022"
enable_swarm: true
monthly_budget: 5.0
First Steps
1. Basic Commands
bashCopy# Interactive mode
thor -i

# Single command
thor -c "list files in current directory"

# With specific model
thor -c "analyze this code" --model opus-4
2. File Operations
bashCopy# In interactive mode
read requirements.txt
write hello.py "print('Hello, World!')"
analyze hello.py
3. Swarm Operations
bashCopy# Start swarm
thor-swarm start --all

# Use swarm
thor -c "create business plan" --use-swarm
Common Use Cases
Code Review
bashCopythor -c "review this Python file for security issues and optimization opportunities" --task-type security
Project Setup
bashCopythor -c "create a new Python project structure with tests, docs, and CI/CD"
Documentation
bashCopythor -c "generate comprehensive documentation for this codebase"
Troubleshooting
API Key Issues
bashCopy# Check if set
echo $ANTHROPIC_API_KEY

# Set for current session
export ANTHROPIC_API_KEY="your_key"

# Set permanently (add to ~/.bashrc or ~/.zshrc)
echo 'export ANTHROPIC_API_KEY="your_key"' >> ~/.bashrc
Permission Issues
bashCopy# Fix permissions
chmod +x thor/src/thor_main.py
chmod +x start_thor.sh
Package Issues
bashCopy# Reinstall packages
pip install --force-reinstall -r requirements.txt

# Clear cache
pip cache purge
Memory Issues
bashCopy# Limit memory usage
thor -i --max-memory 1GB

---

**THOR - Because development should be as powerful as the god of thunder.** ⚡

