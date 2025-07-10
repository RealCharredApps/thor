# src/thor_main.py
import asyncio
import argparse
import sys
import os
from pathlib import Path
import signal
import threading
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from core.thor_client import ThorClient
from core.config import ConfigManager

class ThorCLI:
    """Enhanced CLI interface with advanced features"""
    
    def __init__(self):
        self.client: Optional[ThorClient] = None
        self.running = True
        self.session_id = "default"
        
    async def initialize(self):
        """Initialize THOR client"""
        try:
            print("🚀 Initializing THOR...")
            self.client = ThorClient()
            await self.client.initialize()
            print("✅ THOR initialized successfully!")
            print(f"💰 Budget: ${self.client.config_manager.config.max_daily_spend:.2f}/day")
            print(f"🤖 Swarm: {'Enabled' if self.client.config_manager.config.enable_swarm else 'Disabled'}")
            print("📘 Type 'help' for available commands, 'quit' to exit")
            print("🛑 Press Ctrl+C to interrupt long operations")
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Failed to initialize THOR: {e}")
            sys.exit(1)
    
    async def run_interactive(self):
        """Run interactive mode"""
        await self.initialize()
        
        while self.running:
            try:
                user_input = input(f"\n🤖 THOR [{self.session_id}]: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                elif user_input.startswith('session '):
                    self.session_id = user_input.split(' ', 1)[1]
                    print(f"📝 Switched to session: {self.session_id}")
                    continue
                elif user_input.lower() == 'cost':
                    result = self.client._tool_cost_check()
                    print(result)
                    continue
                elif user_input.lower() == 'swarm':
                    if self.client.swarm_manager.orchestrator:
                        status = await self.client.swarm_manager.orchestrator.get_swarm_status()
                        print(f"🤖 Swarm Status: {status}")
                    else:
                        print("❌ Swarm not enabled")
                    continue
                
                # Process with THOR
                response = await self.client.chat(user_input, self.session_id)
                print(f"\n{response}")
                
            except KeyboardInterrupt:
                print("\n🛑 Operation interrupted by user")
                self.client.kill_flag.set()
                continue
            except EOFError:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n👋 Goodbye!")
        if self.client:
            await self.client._shutdown()
    
    def show_help(self):
        """Show help information"""
        print("""
🤖 THOR - Advanced AI Development Assistant

BASIC COMMANDS:
  help                 - Show this help
  quit                 - Exit THOR
  cost                 - Check API usage and costs
  swarm                - Check swarm status
  session <name>       - Switch to different session

SWARM COMMANDS:
  Deploy agents: "deploy legal agent for contract review"
  Orchestrate: "use business and legal agents to analyze this contract"
  
DEVELOPMENT COMMANDS:
  File operations: "read file.py", "write code to app.py"
  Code analysis: "analyze the code structure"
  Command execution: "run npm install"
  
ADVANCED FEATURES:
  🧠 Memory persistence across sessions
  💰 Cost optimization and budget tracking
  🤖 Multi-agent swarm coordination
  🛑 Kill switch for long operations
  📊 Code analysis and best practices
  
EXAMPLES:
  "Create a Python web scraper for news articles"
  "Analyze this contract using legal and business agents"
  "Review the security of my authentication system"
  "Optimize this code for better performance"
        """)
    
    async def run_single_command(self, command: str):
        """Run single command and exit"""
        await self.initialize()
        response = await self.client.chat(command, self.session_id)
        print(response)
        await self.client._shutdown()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="THOR - Advanced AI Development Assistant")
    parser.add_argument("--command", "-c", help="Run single command and exit")
    parser.add_argument("--session", "-s", default="default", help="Session ID")
    parser.add_argument("--config", help="Config file path")
    
    args = parser.parse_args()
    
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