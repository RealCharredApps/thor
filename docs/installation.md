# THOR Installation Guide

## System Requirements

- **Python**: 3.8 or higher
- **Node.js**: 16+ (for MCP servers)
- **npm**: Latest version
- **Git**: For version control
- **Operating System**: macOS, Linux, or Windows

## Quick Installation

1. **Clone THOR:**
   ```bash
   git clone <your-repo-url>
   cd thor
   ```

2. **Run setup script:**
   ```bash
   python scripts/setup.py
   ```

3. **Set your API key:**
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

4. **Quick start:**
   ```bash
   ./scripts/quickstart.sh my-project
   ```

## Manual Installation

### 1. Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. MCP Servers

```bash
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-git
npm install -g @modelcontextprotocol/server-sqlite
```

### 3. Configuration

```bash
cp config/config.example.yml config/config.yml
# Edit config.yml with your settings
```

### 4. Make THOR executable

```bash
chmod +x thor
```

## API Key Setup

### Option 1: Environment Variable (Recommended)
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Add to your shell profile (`.bashrc`, `.zshrc`, etc.) for persistence:
```bash
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
```

### Option 2: Configuration File
Edit `config/config.yml`:
```yaml
anthropic:
  api_key: "your-api-key-here"
```

## Verification

Test your installation:
```bash
./thor version
./thor agents
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   chmod +x thor
   chmod +x scripts/*.py
   chmod +x scripts/*.sh
   ```

2. **MCP Server Installation Fails**
   - Ensure Node.js 16+ is installed
   - Try using npx instead of global installation
   - Check npm permissions

3. **Python Module Import Errors**
   - Verify Python 3.8+ is being used
   - Install dependencies in a virtual environment:
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     pip install -r requirements.txt
     ```

4. **API Key Issues**
   - Verify your Anthropic API key is correct
   - Check that the key has sufficient credits
   - Ensure the key is properly exported or in config

### Getting Help

- Check the logs: `tail -f logs/thor.log`
- Run with debug mode: `THOR_DEBUG=1 ./thor chat project-path`
- Review the example scripts in `scripts/`

## Next Steps

Once installed, proceed to:
- [Configuration Guide](configuration.md)
- [Quick Start Tutorial](quickstart.md)
- [API Reference](api.md)
