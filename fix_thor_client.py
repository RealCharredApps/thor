import fileinput
import sys

# Read the file and fix the incomplete chat method
with open('src/core/thor_client.py', 'r') as f:
    lines = f.readlines()

# Find where the error is (around line 423)
fixed_lines = []
in_chat_method = False
indent_level = 0

for i, line in enumerate(lines):
    if 'async def chat(self' in line:
        in_chat_method = True
        indent_level = len(line) - len(line.lstrip())
    
    # Check if we're at the problematic area
    if i == 423 and in_chat_method:
        # Add the missing method body
        fixed_lines.append(line)
        fixed_lines.append(' ' * (indent_level + 4) + '"""Main chat interface"""\n')
        fixed_lines.append(' ' * (indent_level + 4) + 'return "Chat method needs implementation"\n')
        continue
    
    fixed_lines.append(line)

# Write the fixed file
with open('src/core/thor_client.py', 'w') as f:
    f.writelines(fixed_lines)

print("Fixed syntax error in thor_client.py")
