THOR Command Cheatsheet
markdownCopy# thor/THOR_CHEATSHEET.md

# 🔨 THOR AI Development Assistant - Command Cheatsheet

## Quick Start Commands

### Installation & Setup
```bash
# Clone and setup
git clone https://github.com/RealCharredApps/thor.git
cd thor
make setup              # Full setup with dependencies
make install           # Install dependencies only

# Alternative setup
pip install -r requirements.txt
pip install -e .
Environment Setup
bashCopy# Set API key
export ANTHROPIC_API_KEY="your_api_key_here"

# Or create .env file
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
Core Commands
Interactive Mode
bashCopy# Start interactive chat
thor --interactive
thor -i

# Start with specific model
thor -i --model opus-4
thor -i --model sonnet-4

# Start with session ID
thor -i --session my-session-001
Single Command Mode
bashCopy# Execute single command
thor --command "analyze this code file"
thor -c "create a Python script for web scraping"

# With specific task type
thor -c "debug this function" --task-type coding
thor -c "review architecture" --task-type architecture
Swarm Commands
bashCopy# Start swarm orchestrator
thor-swarm start

# Start all agents
thor-swarm start --all

# Start specific agent
thor-swarm start --agent-type business
thor-swarm start --agent-type legal

# Stop swarm
thor-swarm stop --all

# Check swarm status
thor-swarm status

# Deploy new agent
thor-swarm deploy --agent-type science
Interactive Mode Commands
Basic Controls
Copyhelp                    # Show available commands
status                  # Show system status
exit, quit, bye         # Exit THOR
clear                   # Clear screen
Emergency Controls
Copykill                    # Emergency stop all operations
reset                   # Reset kill switch
pause                   # Pause current operation
resume                  # Resume paused operation
Session Management
Copysave                    # Save current conversation
load <session_id>       # Load previous conversation
sessions                # List all sessions
export markdown         # Export conversation to markdown
File Operations
Copyread <file_path>        # Read file content
write <file_path>       # Write content to file
list <directory>        # List files in directory
analyze <file_path>     # Analyze code file
search <pattern>        # Search files for pattern
Agent Operations
Copydeploy <agent_type>     # Deploy new agent
swarm <task>            # Execute task with swarm
agents list             # List active agents
agent status <id>       # Get agent status
Advanced Usage
Model Selection
bashCopy# Force specific model
thor -c "complex analysis" --model opus-4

# Auto-selection based on task
thor -c "quick fix" --task-type coding     # Uses sonnet-4
thor -c "architecture review" --task-type architecture  # Uses opus-4
Parallel Execution
bashCopy# Multiple tasks in parallel
thor -c "analyze file1.py && analyze file2.py" --parallel

# Multiple sessions
thor -i --session session1 &
thor -i --session session2 &
Configuration
bashCopy# Use custom config
thor -c "test command" --config custom_config.yaml

# Override specific settings
thor -c "test" --max-tokens 8192 --temperature 0.9
Keyboard Shortcuts (Interactive Mode)
Navigation

Ctrl+C - Interrupt current operation
Ctrl+D - Exit THOR
Ctrl+L - Clear screen
Ctrl+R - Search command history

Editing

Ctrl+A - Move to beginning of line
Ctrl+E - Move to end of line
Ctrl+K - Delete to end of line
Ctrl+U - Delete entire line

Emergency

Ctrl+C twice - Force kill switch
Ctrl+Z - Suspend (use fg to resume)

Error Handling
Common Issues
bashCopy# API key not set
export ANTHROPIC_API_KEY="your_key"

# Permission denied
chmod +x thor/src/thor_main.py

# Port already in use (swarm)
thor-swarm stop --all
lsof -ti:8000-8010 | xargs kill -9

# Memory issues
thor --max-memory 2GB
Recovery Commands
bashCopy# Reset everything
thor reset --all

# Clear memory
thor clear --memory

# Restart swarm
thor-swarm restart --all
Performance Optimization
Resource Management
bashCopy# Limit memory usage
thor -i --max-memory 1GB

# Limit concurrent tasks
thor -c "task" --max-parallel 2

# Enable resource monitoring
thor -i --monitor-resources
Cost Control
bashCopy# Set budget limit
thor -i --budget 5.00

# Use cost-efficient models
thor -i --prefer-efficiency

# Check usage
thor usage --monthly
Integration Commands
Argus Integration
bashCopy# Test Argus connection
thor test-argus

# Sync with Argus
thor sync-argus

# Import Argus agents
thor import-agents --source argus
External Tools
bashCopy# Run with VS Code
code . && thor -i

# Integration with Git
thor -c "analyze git diff"

# Docker integration
thor -c "containerize this project"
Debugging
Verbose Mode
bashCopy# Enable debug logging
thor -i --debug

# Trace mode
thor -i --trace

# Save debug logs
thor -i --log-file debug.log
Health Checks
bashCopy# System health
thor health

# Agent health
thor-swarm health

# Connection tests
thor test-connections
Examples
Quick Tasks
bashCopy# Code review
thor -c "review this Python file for security issues" --task-type security

# Generate documentation
thor -c "create README for this project" --task-type documentation

# Refactor code
thor -c "refactor this function to be more efficient" --task-type coding
Complex Workflows
bashCopy# Multi-agent analysis
thor-swarm start --all
thor -c "analyze business requirements and create technical architecture" --use-swarm

# Research project
thor -c "research AI trends and create market analysis" --agents business,science
Tips & Best Practices
Performance Tips

Use sonnet-4 for most tasks (cost-effective)
Use opus-4 only for complex analysis
Enable kill switch for long operations
Use parallel execution for independent tasks

Security Tips

Never commit API keys to git
Use environment variables for secrets
Regularly rotate API keys
Monitor API usage and costs

Workflow Tips

Save important conversations
Use descriptive session names
Break complex tasks into smaller parts
Use swarm for multi-domain tasks