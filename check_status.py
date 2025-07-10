#!/usr/bin/env python3
"""
THOR Debug and Status Script
Check the status of your Thor installation
"""
import os
import sys
import subprocess
from pathlib import Path

# Colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_file(path, description):
    """Check if a file exists and report status"""
    if Path(path).exists():
        size = Path(path).stat().st_size
        print(f"{GREEN}✅{RESET} {description} ({size:,} bytes)")
        return True
    else:
        print(f"{RED}❌{RESET} {description} - NOT FOUND")
        return False

def main():
    base_dir = Path(__file__).parent
    print(f"\n{BLUE}🔨 THOR Installation Status{RESET}")
    print("=" * 50)
    
    # Check core files
    print(f"\n{YELLOW}Core Files:{RESET}")
    check_file(base_dir / "thor", "Main executable")
    check_file(base_dir / "requirements.txt", "Python requirements")
    check_file(base_dir / "package.json", "Node.js packages")
    
    # Check source files
    print(f"\n{YELLOW}Source Files:{RESET}")
    check_file(base_dir / "src/thor_main.py", "Main application")
    check_file(base_dir / "src/core/thor_client.py", "Thor client")
    check_file(base_dir / "src/tools/advanced_tools.py", "Advanced tools")
    
    # Check scripts
    print(f"\n{YELLOW}Scripts:{RESET}")
    check_file(base_dir / "scripts/setup.py", "Setup script")
    check_file(base_dir / "scripts/quickstart.sh", "Quick start script")
    
    # Check Python
    print(f"\n{YELLOW}Environment:{RESET}")
    print(f"{GREEN}✅{RESET} Python {sys.version.split()[0]}")
    
    # Check Node
    try:
        node_version = subprocess.check_output(['node', '--version'], text=True).strip()
        print(f"{GREEN}✅{RESET} Node.js {node_version}")
    except:
        print(f"{YELLOW}⚠️{RESET}  Node.js not found (MCP servers won't work)")
    
    # Check API key
    if os.environ.get('ANTHROPIC_API_KEY'):
        print(f"{GREEN}✅{RESET} Anthropic API key is set")
    else:
        print(f"{RED}❌{RESET} Anthropic API key NOT set")
        print(f"   Run: export ANTHROPIC_API_KEY='your-key-here'")
    
    print(f"\n{YELLOW}Next Steps:{RESET}")
    print("1. Make scripts executable:")
    print(f"   chmod +x {base_dir}/scripts/setup.py")
    print(f"   chmod +x {base_dir}/scripts/quickstart.sh") 
    print(f"   chmod +x {base_dir}/thor")
    print("\n2. Run setup:")
    print(f"   cd {base_dir}")
    print("   python3 scripts/setup.py")
    print("\n3. Set API key if not done:")
    print("   export ANTHROPIC_API_KEY='your-key-here'")
    print("\n4. Start using Thor:")
    print("   ./scripts/quickstart.sh my-project")
    print("   # or")
    print("   ./thor chat my-project")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
