# THOR Quick Start Guide

Get up and running with THOR in minutes!

## Prerequisites

- Python 3.8+
- Node.js 16+ (for MCP servers)
- Anthropic API key

## 1. Installation

```bash
# Clone THOR
git clone <your-repo-url>
cd thor

# Run setup
python scripts/setup.py

# Set API key
export ANTHROPIC_API_KEY="your-api-key-here"
```

## 2. Quick Start

### Option A: New Project
```bash
./scripts/quickstart.sh my-awesome-project
```

### Option B: Existing Project
```bash
# Setup THOR for existing project
./thor setup /path/to/your/project

# Start development
./thor chat /path/to/your/project
```

## 3. Basic Usage

### Interactive Chat
```bash
./thor chat /path/to/project
```

Once in chat mode:
- Ask questions: "How can I improve the performance of this code?"
- Request features: "Create a user authentication system with JWT"
- Get analysis: "Perform a security audit of this application"
- Switch agents: `/agent security_guardian`
- Enable autonomous mode: `/autonomous`

### Build Complete Projects
```bash
# Build a FastAPI application
./thor build /path/to/project --type fastapi --features "auth,database,api"

# Build a React application  
./thor build /path/to/project --type react --features "routing,state-management"
```

### Analyze Projects
```bash
# Full analysis
./thor analyze /path/to/project --type full

# Security audit
./thor analyze /path/to/project --type security

# Performance analysis
./thor analyze /path/to/project --type performance
```

## 4. Expert Agents

THOR includes specialized AI agents:

- **thor_architect**: Master architect for complex projects
- **code_wizard**: Expert programmer for implementation
- **devops_master**: DevOps expert for infrastructure
- **security_guardian**: Security expert for protection
- **ai_specialist**: AI/ML expert for intelligent features

Switch agents in chat: `/agent code_wizard`

## 5. Example Workflows

### Creating a Full-Stack App
```bash
# Setup new project
./thor setup my-saas-app

# Start chat and ask:
./thor chat my-saas-app
```

Then in chat:
```
Create a complete SaaS application with:
- FastAPI backend with JWT authentication
- React frontend with modern UI
- PostgreSQL database with proper schema
- Docker deployment configuration
- Comprehensive testing suite
- CI/CD pipeline setup
```

### Code Review and Optimization
```bash
# Analyze existing project
./thor chat existing-project
```

Then ask:
```
Perform a comprehensive code review of this project and:
1. Identify performance bottlenecks
2. Find security vulnerabilities
3. Suggest architecture improvements
4. Generate missing tests
5. Optimize database queries
```

### Autonomous Development
Enable autonomous mode for complex multi-step tasks:
```bash
./thor chat project --auto
```

Then request:
```
Build a complete e-commerce backend with:
- Product catalog with search
- User authentication and profiles
- Shopping cart and checkout
- Payment integration
- Order management
- Admin dashboard
- API documentation
- Deployment scripts

Work autonomously and complete all tasks.
```

## 6. Configuration

Customize THOR by editing `config/config.yml`:

```yaml
anthropic:
  model: "claude-3-5-sonnet-20241022"  # or claude-3-opus-20240229
  temperature: 0.3  # Lower for more focused, higher for creative

autonomous:
  enabled: true
  max_parallel_tasks: 5  # Increase for faster execution
  auto_commit: true  # Automatically commit changes
```

## 7. Tips for Best Results

### Be Specific
❌ "Make this better"
✅ "Optimize this function for performance, add error handling, and improve readability"

### Use Autonomous Mode for Complex Tasks
❌ Breaking complex tasks into many small requests
✅ Asking for complete features and enabling autonomous mode

### Leverage Expert Agents
❌ Using thor_architect for simple coding tasks
✅ Using code_wizard for implementation, security_guardian for audits

### Provide Context
❌ "Fix this bug"
✅ "Fix the authentication bug where users can't login after password reset. The error occurs in auth.py line 45."

## 8. Common Commands

```bash
# Show available agents
./thor agents

# Show version
./thor version

# Setup new project
./thor setup /path/to/project

# Interactive development
./thor chat /path/to/project

# Build project from scratch
./thor build /path/to/project --type python

# Comprehensive analysis
./thor analyze /path/to/project --type full
```

## Next Steps

- [Configuration Guide](configuration.md) - Customize THOR
- [API Reference](api.md) - Programmatic usage  
- [Expert Agents](agents.md) - Learn about AI specialists
- [Examples](examples.md) - See more examples

## Getting Help

- Check logs: `tail -f logs/thor.log`
- Enable debug: `THOR_DEBUG=1 ./thor chat project`
- Review examples: `scripts/example_usage.py`

**THOR is ready to revolutionize your development workflow! 🚀**
