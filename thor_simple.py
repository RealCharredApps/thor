# thor_simple.py (ROOT LEVEL - SIMPLE VERSION)
#!/usr/bin/env python3
"""
THOR - Simple AI Assistant
Ultra-simple version that just works
"""

import os
import sys
import asyncio
from datetime import datetime

# Check for required package
try:
    import anthropic
except ImportError:
    print("❌ Missing required package. Install with:")
    print("   pip install anthropic")
    sys.exit(1)

class SimpleTHOR:
    """Simple THOR that actually works"""
    
    def __init__(self):
        # Get API key
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            print("❌ ANTHROPIC_API_KEY not set")
            print("Set it with: export ANTHROPIC_API_KEY='your_key_here'")
            sys.exit(1)
        
        # Initialize client
        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            print("✅ THOR initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize: {e}")
            sys.exit(1)
    
    async def chat(self, message: str) -> str:
        """Simple chat function"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4000,
                    messages=[{
                        "role": "user", 
                        "content": message
                    }]
                )
            )
            return response.content[0].text
        except Exception as e:
            return f"Error: {str(e)}"
    
    def run_interactive(self):
        """Interactive mode"""
        print("🔨 THOR AI Assistant")
        print("Type 'exit' to quit, 'help' for commands")
        print("-" * 40)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                print("\n🤖 THOR: ", end="", flush=True)
                
                # Get response
                response = asyncio.run(self.chat(user_input))
                print(response)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def show_help(self):
        """Show help"""
        print("""
🔨 THOR Commands:
  help    - Show this help
  exit    - Exit THOR
  
💡 Just type naturally - THOR will respond!
Examples:
  "What is Python?"
  "Write a hello world program"
  "Explain machine learning"
        """)

def main():
    """Main function"""
    print("🔨 Starting THOR...")
    
    # Simple argument handling
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("""
🔨 THOR - Simple AI Assistant

Usage:
  python thor_simple.py              # Interactive mode
  python thor_simple.py "question"   # Single question

Setup:
  1. Install: pip install anthropic
  2. Set key: export ANTHROPIC_API_KEY='your_key'
  3. Run: python thor_simple.py
            """)
            return
        
        # Single question mode
        thor = SimpleTHOR()
        question = " ".join(sys.argv[1:])
        print(f"💬 Question: {question}")
        print("🤖 THOR: ", end="", flush=True)
        response = asyncio.run(thor.chat(question))
        print(response)
    else:
        # Interactive mode
        thor = SimpleTHOR()
        thor.run_interactive()

if __name__ == "__main__":
    main()  