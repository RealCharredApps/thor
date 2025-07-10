import os
import stat
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.thor_main import main

if __name__ == '__main__':
    main()

# Make scripts executable
script_files = [
    '/Users/bbm2/Documents/GitHub/thor/thor',
    '/Users/bbm2/Documents/GitHub/thor/scripts/setup.py',
    '/Users/bbm2/Documents/GitHub/thor/scripts/example_usage.py',
    '/Users/bbm2/Documents/GitHub/thor/scripts/quickstart.sh'
]

for script_file in script_files:
    try:
        # Get current permissions
        current_permissions = os.stat(script_file).st_mode
        
        # Add execute permission for owner, group, and others
        new_permissions = current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        
        # Set new permissions
        os.chmod(script_file, new_permissions)
        print(f"Made executable: {script_file}")
    except Exception as e:
        print(f"Error making {script_file} executable: {e}")

print("All scripts are now executable!")
