# src/macos/thor_app.py - UPDATED
import os
import subprocess
import sys
from pathlib import Path

def create_thor_app():
    """Create a proper macOS app for THOR"""
    
    # Get the current THOR directory
    thor_dir = Path(__file__).parent.parent.parent
    
    # Create app structure
    app_path = Path.home() / "Applications" / "THOR.app"
    contents_path = app_path / "Contents"
    macos_path = contents_path / "MacOS"
    resources_path = contents_path / "Resources"
    
    # Create directories
    macos_path.mkdir(parents=True, exist_ok=True)
    resources_path.mkdir(parents=True, exist_ok=True)
    
    # Info.plist
    info_plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>THOR</string>
    <key>CFBundleIdentifier</key>
    <string>com.realcharredapps.thor</string>
    <key>CFBundleName</key>
    <string>THOR AI Assistant</string>
    <key>CFBundleDisplayName</key>
    <string>THOR</string>
    <key>CFBundleVersion</key>
    <string>2.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>"""
    
    with open(contents_path / "Info.plist", "w") as f:
        f.write(info_plist)
    
    # Main executable script
    executable_script = f"""#!/bin/bash
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
cd "{thor_dir}"

# Check if virtual environment exists
if [ ! -d "thor_env" ]; then
    osascript -e 'display dialog "THOR environment not found. Please run installation first." with title "THOR Error"'
    exit 1
fi

# Source shell profile for environment variables
if [ -f "$HOME/.zshrc" ]; then
    source "$HOME/.zshrc"
elif [ -f "$HOME/.bash_profile" ]; then
    source "$HOME/.bash_profile"
fi

# Activate virtual environment
source thor_env/bin/activate

# Check if API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    osascript -e 'display dialog "ANTHROPIC_API_KEY not set.\\n\\nPlease add to your shell profile:\\nexport ANTHROPIC_API_KEY='"'"'your_key_here'"'"'" with title "THOR Setup Required"'
    exit 1
fi

# Launch THOR in a new terminal
osascript -e 'tell app "Terminal" to do script "cd \\"{thor_dir}\\" && source thor_env/bin/activate && thor"'
"""
    
    executable_path = macos_path / "THOR"
    with open(executable_path, "w") as f:
        f.write(executable_script)
    
    # Make executable
    os.chmod(executable_path, 0o755)
    
    print(f"✅ THOR app created at: {app_path}")
    print("🔄 The app will open THOR in a new Terminal window")
    print("💡 You can now find THOR in your Applications folder")
    
    return app_path

if __name__ == "__main__":
    create_thor_app()