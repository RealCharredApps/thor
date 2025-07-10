# thor/src/thor_main.py
import asyncio
import argparse
import sys
import os
from pathlib import Path
import logging
from typing import Optional
import signal
import threading
from dataclasses import dataclass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from core.thor_client import ThorClient, ThorConfig
from utils.model_selector import ModelSelector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ThorCLI:
    """THOR Command Line Interface"""
    
    def __init__(self):
        self.thor_client: Optional[ThorClient] = None
        self.running = False
        self.shutdown_event = threading.Event()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Shutdown signal received")
        self.shutdown_event.set()
        if self.thor_client:
            self.thor_client.kill_switch.set()
        sys.exit(0)
    
    def _load_config(self) -> ThorConfig:
        """Load configuration"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable required")
        
        return ThorConfig(
            anthropic_api_key=api_key,
            enable_swarm=True,
            parallel_sessions=True,
            auto_save_conversations=True,
            kill_switch_enabled=True
        )
    
    async def start_interactive_mode(self):
        """Start interactive chat mode"""
        print("🔨 THOR AI Development Assistant")
        print("Type 'help' for commands, 'exit' to quit, 'kill' for emergency stop")
        print("=" * 60)
        
        config = self._load_config()
        self.thor_client = ThorClient(config)
        
        while not self.shutdown_event.is_set():
            try:
                user_input = input("\n💬 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    break
                
                if user_input.lower() == 'kill':
                    await self.thor_client._tool_kill_switch({"reason": "User requested"})
                    print("⚠️  Kill switch activated!")
                    continue
                
                if user_input.lower() == 'reset':
                    self.thor_client.reset_kill_switch()
                    print("✅ Kill switch reset")
                    continue
                
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if user_input.lower() == 'status':
                    await self._show_status()
                    continue
                
                # Determine task type for model selection
                task_type = self._determine_task_type(user_input)
                
                print(f"\n🤖 THOR (using {task_type} model):")
                
                # Process message
                response = await self.thor_client.process_message(user_input, task_type)
                
                if response.get("error"):
                    print(f"❌ Error: {response['error']}")
                else:
                    # Display response
                    if "response" in response:
                        resp_data = response["response"]
                        
                        if "content" in resp_data:
                            print(resp_data["content"])
                        
                        if "tool_results" in resp_data:
                            print("\n📋 Tool Results:")
                            for result in resp_data["tool_results"]:
                                print(f"  • {result['tool']}: {result.get('output', result.get('error', 'No output'))}")
                    
                    # Show usage info
                    if "processing_time" in response:
                        print(f"\n⏱️  Processing time: {response['processing_time']:.2f}s")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                logger.error(f"Interactive mode error: {str(e)}")
    
    def _determine_task_type(self, user_input: str) -> str:
        """Determine task type from user input"""
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ['code', 'debug', 'fix', 'implement', 'write code']):
            return 'coding'
        elif any(word in input_lower for word in ['architecture', 'design', 'security', 'audit']):
            return 'architecture'
        elif any(word in input_lower for word in ['complex', 'analyze', 'research', 'deep']):
            return 'complex_analysis'
        else:
            return 'general'
    
    def _show_help(self):
        """Show help information"""
        help_text = """
🔨 THOR Commands:
  help        - Show this help
  status      - Show system status
  kill        - Emergency stop all operations
  reset       - Reset kill switch
  exit/quit   - Exit THOR
  
🤖 Available Tools:
  • File operations (read, write, create, list)
  • Code analysis and execution
  • Swarm orchestration
  • Artifact management
  • Parallel task execution
  
💡 Tips:
  • Use specific terms like 'code', 'debug', 'architecture' for better model selection
  • THOR automatically saves conversations
  • Use 'kill' command to stop long-running operations
  • Type naturally - THOR understands context
        """
        print(help_text)
    
    async def _show_status(self):
        """Show system status"""
        if not self.thor_client:
            print("❌ THOR not initialized")
            return
        
        print("\n📊 THOR Status:")
        print(f"  • Session: {self.thor_client.session_id}")
        print(f"  • Kill switch: {'🔴 Active' if self.thor_client.kill_switch.is_set() else '🟢 Ready'}")
        print(f"  • Running: {'🔄 Yes' if self.thor_client.is_running else '⏸️  No'}")
        
        # Conversation stats
        conv_summary = self.thor_client.conversation_memory.get_summary()
        print(f"  • Messages: {conv_summary['message_count']}")
        
        # Swarm status
        if self.thor_client.swarm_manager:
            swarm_status = await self.thor_client.swarm_manager.get_status()
            print(f"  • Agents: {swarm_status['agents']['total']}")
            print(f"  • Tasks: {swarm_status['tasks']['total']}")
    
    async def run_single_command(self, command: str, task_type: str = "general"):
        """Run a single command and exit"""
        config = self._load_config()
        config.auto_save_conversations = False
        
        thor_client = ThorClient(config)
        
        try:
            response = await thor_client.process_message(command, task_type)
            
            if response.get("error"):
                print(f"Error: {response['error']}")
                return 1
            
            if "response" in response:
                resp_data = response["response"]
                
                if "content" in resp_data:
                    print(resp_data["content"])
                
                if "tool_results" in resp_data:
                    for result in resp_data["tool_results"]:
                        if "output" in result:
                            print(result["output"])
            
            return 0
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return 1

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="THOR AI Development Assistant")
    parser.add_argument("--command", "-c", help="Single command to execute")
    parser.add_argument("--task-type", "-t", default="general", 
                       choices=["general", "coding", "architecture", "complex_analysis"],
                       help="Task type for model selection")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Start interactive mode")
    
    args = parser.parse_args()
    
    cli = ThorCLI()
    
    try:
        if args.command:
            return asyncio.run(cli.run_single_command(args.command, args.task_type))
        else:
            asyncio.run(cli.start_interactive_mode())
            return 0
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 0
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())