# thor/check_repo.py
import os
import json
import subprocess
from pathlib import Path

def check_thor_repo():
    """Check THOR repository structure and dependencies"""
    print("🔍 Checking THOR Repository Status")
    print("=" * 50)
    
    # Check directory structure
    required_dirs = [
        "src/core",
        "src/agents", 
        "src/utils",
        "src/config",
        "config",
        "tests",
        "docs"
    ]
    
    print("\n📁 Directory Structure:")
    for directory in required_dirs:
        exists = os.path.exists(directory)
        status = "✅" if exists else "❌"
        print(f"  {status} {directory}")
    
    # Check key files
    required_files = [
        "requirements.txt",
        "setup.py",
        "README.md",
        "src/thor_main.py",
        "src/core/thor_client.py",
        ".env"
    ]
    
    print("\n📄 Key Files:")
    for file in required_files:
        exists = os.path.exists(file)
        status = "✅" if exists else "❌"
        print(f"  {status} {file}")
    
    # Check Python environment
    print("\n🐍 Python Environment:")
    try:
        result = subprocess.run(["python", "--version"], capture_output=True, text=True)
        print(f"  Python: {result.stdout.strip()}")
    except:
        print("  ❌ Python not found")
    
    try:
        result = subprocess.run(["pip", "--version"], capture_output=True, text=True)
        print(f"  Pip: {result.stdout.strip()}")
    except:
        print("  ❌ Pip not found")
    
    # Check dependencies
    print("\n📦 Dependencies:")
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            requirements = f.read().strip().split("\n")
        
        for req in requirements:
            if req.strip():
                package_name = req.split(">=")[0].split("==")[0].split("~=")[0]
                try:
                    result = subprocess.run(
                        ["pip", "show", package_name], 
                        capture_output=True, 
                        text=True
                    )
                    if result.returncode == 0:
                        print(f"  ✅ {package_name}")
                    else:
                        print(f"  ❌ {package_name} (not installed)")
                except:
                    print(f"  ❓ {package_name} (check failed)")
    
    # Check environment variables
    print("\n🔑 Environment Variables:")
    env_vars = ["ANTHROPIC_API_KEY", "THOR_LOG_LEVEL", "THOR_ENABLE_SWARM"]
    for var in env_vars:
        value = os.getenv(var)
        if value:
            masked_value = f"{value[:10]}..." if len(value) > 10 else value
            print(f"  ✅ {var}: {masked_value}")
        else:
            print(f"  ❌ {var}: Not set")
    
    # Check Git status
    print("\n📊 Git Status:")
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.returncode == 0:
            changes = result.stdout.strip()
            if changes:
                print(f"  📝 Uncommitted changes: {len(changes.split())}")
            else:
                print("  ✅ Working directory clean")
        else:
            print("  ❌ Not a git repository")
    except:
        print("  ❓ Git check failed")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    check_repo()