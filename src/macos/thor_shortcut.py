# src/macos/thor_shortcut.py
import subprocess
import sys
from pathlib import Path

def create_macos_shortcut():
    """Create macOS application shortcut"""
    app_name = "THOR"
    thor_path = Path(__file__).parent.parent.parent
    
    # Create app bundle structure
    app_path = Path(f"/Applications/{app_name}.app")
    contents_path = app_path / "Contents"
    macos_path = contents_path / "MacOS"
    resources_path = contents_path / "Resources"
    
    # Create directories
    macos_path.mkdir(parents=True, exist_ok=True)
    resources_path.mkdir(parents=True, exist_ok=True)
    
    # Create Info.plist
    info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.realcharredapps.thor</string>
    <key>CFBundleName</key>
    <string>{app_name}</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>"""
    
    with open(contents_path / "Info.plist", "w") as f:
        f.write(info_plist)
    
    # Create executable script
    executable_script = f"""#!/bin/bash
cd "{thor_path}"
python -m src.thor_main
"""
    
    executable_path = macos_path / app_name
    with open(executable_path, "w") as f:
        f.write(executable_script)
    
    # Make executable
    subprocess.run(["chmod", "+x", str(executable_path)])
    
    print(f"✅ Created macOS shortcut: {app_path}")
    print("🔄 You may need to restart Finder or run 'killall Finder'")

if __name__ == "__main__":
    create_macos_shortcut()