# src/thor_multi.py
import asyncio
import sys
import os
from pathlib import Path
import argparse
import threading
import signal
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.session_manager import SessionManager

class MultiSessionThorCLI:
    """Multi-session THOR CLI interface"""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.running = True
        self.current_session = None
        
    def signal_handler(self, signum, frame):
        """Handle graceful shutdown"""
        print(f"\n🛑 Shutting down all sessions...")
        self.running = False
        sys.exit(0)
    
    async def run_interactive(self):
        """Run multi-session interactive mode"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🚀 THOR Multi-Session Manager")
        print("🎯 Each session maintains separate conversation history")
        print("📘 Type 'help' for commands")
        print("-" * 50)
        
        # Create default session
        self.current_session = self.session_manager.create_session("default")
        
        while self.running:
            try:
                session_display = self.current_session[:8] if self.current_session else "none"
                user_input = input(f"\n🤖 THOR [{session_display}]: ").strip()
                
                if not user_input:
                    continue
                
                # Handle session commands
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                elif user_input.lower() == 'quit':
                    break
                elif user_input.startswith('new session'):
                    parts = user_input.split()
                    session_name = parts[2] if len(parts) > 2 else None
                    new_session = self.session_manager.create_session(session_name)
                    self.current_session = new_session
                    print(f"📝 Created and switched to session: {new_session}")
                    continue
                elif user_input.startswith('switch '):
                    session_id = user_input.split(' ', 1)[1]
                    if session_id in self.session_manager.sessions:
                        self.current_session = session_id
                        print(f"🔄 Switched to session: {session_id}")
                    else:
                        # Create new session with this name
                        self.current_session = self.session_manager.create_session(session_id)
                        print(f"📝 Created new session: {session_id}")
                    continue
                elif user_input.lower() == 'list sessions':
                    sessions = self.session_manager.list_sessions()
                    print("\n📋 Active Sessions:")
                    for sid, info in sessions.items():
                        status = "🟢" if info["status"] == "active" else "🔴"
                        current = "← current" if sid == self.current_session else ""
                        print(f"  {status} {sid} - {info['message_count']} messages {current}")
                    continue
                elif user_input.startswith('close '):
                    session_id = user_input.split(' ', 1)[1]
                    if self.session_manager.close_session(session_id):
                        print(f"🗑️  Closed session: {session_id}")
                        if session_id == self.current_session:
                            self.current_session = self.session_manager.create_session("default")
                    else:
                        print(f"❌ Session not found: {session_id}")
                    continue
                
                # Regular chat
                if not self.current_session:
                    self.current_session = self.session_manager.create_session("default")
                
                response = await self.session_manager.chat_with_session(
                    self.current_session, user_input
                )
                print(f"\n{response}")
                
            except KeyboardInterrupt:
                print("\n🛑 Use 'quit' to exit properly")
                continue
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
        
        print("\n👋 All sessions closed. Goodbye!")
    
    def show_help(self):
        """Show help for multi-session commands"""
        print("""
🤖 THOR Multi-Session Manager

SESSION COMMANDS:
  new session [name]    - Create new session (optional name)
  switch <session_id>   - Switch to existing session
  list sessions         - Show all active sessions
  close <session_id>    - Close a session
  quit                  - Exit all sessions

REGULAR COMMANDS:
  All regular THOR commands work within each session:
  - File operations, code analysis, cost checking
  - Each session maintains separate conversation history
  - Session-specific memory and artifacts

EXAMPLES:
  new session project1
  switch project1
  "analyze my React app structure"
  switch default
  "check cost usage"
        """)

async def main():
    """Main entry point for multi-session THOR"""
    parser = argparse.ArgumentParser(description="THOR Multi-Session Manager")
    parser.add_argument("--session", "-s", help="Start with specific session")
    
    args = parser.parse_args()
    
    cli = MultiSessionThorCLI()
    
    if args.session:
        cli.current_session = cli.session_manager.create_session(args.session)
    
    try:
        await cli.run_interactive()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())