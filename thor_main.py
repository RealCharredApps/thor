import asyncio
import argparse
import sys
import os
from pathlib import Path
import signal
import threading
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.thor_client import ThorClient
from core.config import ConfigManager

class ThorCLI:
    """Enhanced CLI interface with better signal handling"""
    
    def __init__(self):
        self.client: Optional[ThorClient] = None
        self.running = True
        self.session_id = "default"
        
    def signal_handler(self, signum, frame):
        """Handle signals properly"""
        print(f"\n🛑 Received interrupt signal. Shutting down gracefully...")
        self.running = False
        if self.client:
            self.client.kill_flag.set()
            self.client.stop_thinking_indicator()
        
        # Force exit after a short delay
        def force_exit():
            import time
            time.sleep(2)
            os._exit(0)
        
        threading.Thread(target=force_exit, daemon=True).start()
        
    async def initialize(self):
        """Initialize THOR client"""
        try:
            print("🚀 Initializing THOR...")
            self.client = ThorClient()
            await self.client.initialize()
            print("✅ THOR initialized successfully!")
            print(f"💰 Budget: ${self.client.config_manager.config.max_daily_spend:.2f}/day")
            print("📘 Type 'help' for available commands, 'quit' to exit")
            print("🛑 Press Ctrl+C to interrupt long operations")
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Failed to initialize THOR: {e}")
            if "ANTHROPIC_API_KEY" in str(e):
                print("💡 Make sure to set your ANTHROPIC_API_KEY environment variable")
                print("💡 Run: export ANTHROPIC_API_KEY='your_key_here'")
            sys.exit(1)
    
    async def run_interactive(self):
        """Run interactive mode"""
        # Set up signal handling
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        await self.initialize()
        
        while self.running:
            try:
                # Get user input
                user_input = input(f"\n🤖 THOR [{self.session_id}]: ").strip()
                
                if not user_input or not self.running:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit']:
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                elif user_input.startswith('session '):
                    parts = user_input.split(' ', 1)
                    if len(parts) > 1:
                        self.session_id = parts[1]
                        print(f"📝 Switched to session: {self.session_id}")
                    continue
                elif user_input.lower() == 'cost':
                    result = self.client._tool_cost_check()
                    print(result)
                    continue
                elif user_input.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                elif user_input.lower() == 'status':
                    result = self.client._tool_swarm_status()
                    print(result)
                    continue
                
                # Process with THOR
                response = await self.client.chat(user_input, self.session_id)
                print(f"\n{response}")
                
            except KeyboardInterrupt:
                print("\n🛑 Operation interrupted")
                if self.client:
                    self.client.kill_flag.set()
                    self.client.stop_thinking_indicator()
                continue
            except EOFError:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
        
        print("\n👋 Goodbye!")
        if self.client:
            self.client.kill_flag.set()
            self.client.stop_thinking_indicator()
    
    def show_help(self):
        """Show help information"""
        print("""
🤖 THOR - Advanced AI Development Assistant

BASIC COMMANDS:
  help                 - Show this help
  quit/exit           - Exit THOR
  cost                 - Check API usage and costs
  status              - Check swarm status
  clear               - Clear terminal
  session <name>       - Switch to different session

DEVELOPMENT COMMANDS:
  "read file.py"              - Read a file
  "write code to app.py"      - Write content to a file
  "list files"                - List files in current directory
  "run ls -la"                - Execute commands
  "analyze code.py"           - Analyze code structure

EXAMPLES:
  "Create a Python web scraper"
  "Review this code for security issues"
  "Optimize my database queries"
  "Help me debug this error"
  
🛑 Press Ctrl+C to interrupt long operations
💡 THOR learns from your coding patterns and preferences
        """)
    
    async def run_single_command(self, command: str):
        """Run single command and exit"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        await self.initialize()
        response = await self.client.chat(command, self.session_id)
        print(response)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="THOR - Advanced AI Development Assistant")
    parser.add_argument("--command", "-c", help="Run single command and exit")
    parser.add_argument("--session", "-s", default="default", help="Session ID")
    parser.add_argument("--config", action="store_true", help="Show configuration")
    
    args = parser.parse_args()
    
    if args.config:
        # Show configuration
        try:
            config = ConfigManager()
            print(f"📁 Config file: thor_config.json")
            print(f"💰 Daily budget: ${config.config.max_daily_spend:.2f}")
            print(f"🤖 Argus path: {config.config.argus_path or 'Not set'}")
            print(f"📝 Log level: {config.config.log_level}")
            return
        except Exception as e:
            print(f"❌ Error reading config: {e}")
            return
    
    cli = ThorCLI()
    cli.session_id = args.session
    
    try:
        if args.command:
            asyncio.run(cli.run_single_command(args.command))
        else:
            asyncio.run(cli.run_interactive())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()