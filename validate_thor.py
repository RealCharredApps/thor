import ast
import sys

try:
    with open('src/core/thor_client.py', 'r') as f:
        content = f.read()
    
    # Try to parse it
    ast.parse(content)
    print("✅ File is syntactically correct!")
    
except SyntaxError as e:
    print(f"❌ Syntax error: {e}")
    print(f"   Line {e.lineno}: {e.text}")
    print(f"   Issue: {e.msg}")
    
    # Try to fix common issues
    if "EOF" in str(e):
        print("\n🔧 Attempting to fix EOF issue...")
        # Make sure file ends with newline
        if not content.endswith('\n'):
            with open('src/core/thor_client.py', 'a') as f:
                f.write('\n')
            print("   Added missing newline at end of file")
    
except Exception as e:
    print(f"❌ Error: {e}")
