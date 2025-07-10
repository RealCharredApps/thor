# scripts/setup.py
#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
from pathlib import Path

def setup_thor():
    """Setup THOR on the system"""
    print("🚀 Setting up THOR AI Development Framework...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Create .thor directory
    thor_dir = Path.home() / '.thor'
    thor_dir.mkdir(exist_ok=True)
    (thor_dir / 'logs').mkdir(exist_ok=True)
    
    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("\n🔑 ANTHROPIC_API_KEY not found in environment")
        print("Please set it using:")
        print("export ANTHROPIC_API_KEY='your-key-here'")
    
    # Create symlink for thor command
    if platform.system() != 'Windows':
        thor_script = Path(__file__).parent.parent / 'thor'
        
        # Make executable
        thor_script.chmod(0o755)
        
        # Try to create symlink in /usr/local/bin
        try:
            link_path = Path('/usr/local/bin/thor')
            if link_path.exists():
                link_path.unlink()
            link_path.symlink_to(thor_script)
            print(f"\n✅ Created command 'thor' in /usr/local/bin")
        except PermissionError:
            print(f"\n⚠️  Could not create global command (needs sudo)")
            print(f"Run: sudo ln -s {thor_script} /usr/local/bin/thor")
    
    print("\n✨ THOR setup complete!")
    print("\nTo get started:")
    print("1. Set your ANTHROPIC_API_KEY environment variable")
    print("2. Run 'thor' to start the interactive assistant")
    print("3. Or use 'thor \"your question here\"' for single queries")

if __name__ == '__main__':
    setup_thor()