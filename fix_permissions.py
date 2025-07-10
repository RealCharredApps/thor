"""
Fix file permissions for THOR scripts
"""
import os
import stat
from pathlib import Path

def make_executable(file_path):
    """Make file executable"""
    try:
        current_permissions = os.stat(file_path).st_mode
        new_permissions = current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        os.chmod(file_path, new_permissions)
        print(f"✅ Made executable: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error making {file_path} executable: {e}")
        return False

# Files to make executable
executable_files = [
    "/Users/bbm2/Documents/GitHub/thor/thor",
    "/Users/bbm2/Documents/GitHub/thor/scripts/setup.py", 
    "/Users/bbm2/Documents/GitHub/thor/scripts/example_usage.py",
    "/Users/bbm2/Documents/GitHub/thor/scripts/quickstart.sh"
]

print("🔨 Making THOR scripts executable...")
success_count = 0

for file_path in executable_files:
    if Path(file_path).exists():
        if make_executable(file_path):
            success_count += 1
    else:
        print(f"⚠️  File not found: {file_path}")

print(f"\n✨ Made {success_count}/{len(executable_files)} files executable!")
print("THOR is ready to use! 🚀")
