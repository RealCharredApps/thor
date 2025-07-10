# THOR - Advanced MCP Client for Autonomous Software Development

THOR is a comprehensive custom MCP (Model Context Protocol) client that replicates and extends Anthropic's console capabilities without throttling limits, specifically designed for autonomous software development on local machines.

## 🚀 Key Features

- **Unlimited Operations**: No throttling limits - complete tasks without interruption
- **Full File System Access**: Read, write, edit, create files and folders on your local machine
- **Custom Prompt Engineering**: Advanced prompt management and expert personas
- **MCP Server Integration**: Connect to any MCP server for extended capabilities
- **Autonomous Development**: Complete features and projects with minimal human intervention
- **Expert AI Agents**: Specialized agents for different development tasks
- **Conversation History**: Persistent chat history with database storage
- **Project Context**: Automatic project understanding and context awareness
- **Production Ready**: Error handling, logging, and enterprise-grade reliability

## 🏗️ Architecture

```
thor/
├── src/
│   ├── core/           # Core client functionality
│   ├── mcp/            # MCP server integrations
│   ├── agents/         # Specialized AI agents
│   ├── tools/          # Development tools
│   └── ui/             # User interface
├── config/             # Configuration files
├── scripts/            # Setup and utility scripts
├── tests/              # Test suite
└── docs/               # Documentation
```

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd thor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
npm install  # For MCP servers
```

3. Configure your API keys:
```bash
cp config/config.example.yml config/config.yml
# Edit config.yml with your API keys
```

4. Run setup script:
```bash
python scripts/setup.py
```

## 🎯 Quick Start

```python
from src.core.thor_client import ThorClient

# Initialize THOR
thor = ThorClient(
    anthropic_api_key="your-api-key",
    project_root="/path/to/your/project"
)

# Start autonomous development
await thor.setup_environment()

# Ask THOR to build something
response = await thor.chat(
    "Create a FastAPI application with JWT authentication",
    expert="backend_architect"
)
```

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [Configuration](docs/configuration.md)
- [API Reference](docs/api.md)
- [Expert Agents](docs/agents.md)
- [Examples](docs/examples.md)

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**THOR** - *Because development should be as powerful as the god of thunder.*
