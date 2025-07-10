# src/core/thor_client.py
import asyncio
import anthropic
import json
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import threading
import signal
import sys

from .config import ConfigManager
from .model_selector import ModelSelector
from .swarm_manager import SwarmManager
from .memory_manager import MemoryManager
from .file_operations import FileOperations

class ThorClient:
    """Enhanced THOR client with swarm capabilities and advanced features"""
    
    def __init__(self, config_path: str = "thor_config.json"):
        self.config_manager = ConfigManager(config_path)
        self.model_selector = ModelSelector(self.config_manager)
        self.swarm_manager = SwarmManager(self.config_manager)
        self.memory_manager = MemoryManager(self.config_manager)
        self.file_ops = FileOperations()
        
        self.client = anthropic.Anthropic(api_key=self.config_manager.config.api_key)
        self.logger = logging.getLogger(__name__)
        
        # State management
        self.active_sessions = {}
        self.kill_flag = threading.Event()
        self.thinking_indicator = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Initialize enhanced system prompt
        self.system_prompt = self._build_enhanced_system_prompt()
        
        # Tools registry
        self.tools = {
            'read_file': self._tool_read_file,
            'write_file': self._tool_write_file,
            'list_files': self._tool_list_files,
            'create_directory': self._tool_create_directory,
            'run_command': self._tool_run_command,
            'search_files': self._tool_search_files,
            'analyze_code': self._tool_analyze_code,
            'orchestrate_swarm': self._tool_orchestrate_swarm,
            'deploy_agent': self._tool_deploy_agent,
            'get_swarm_status': self._tool_get_swarm_status,
            'get_memory': self._tool_get_memory,
            'save_artifact': self._tool_save_artifact,
            'cost_check': self._tool_cost_check
        }
    
    def _build_enhanced_system_prompt(self) -> str:
        """Build comprehensive system prompt with swarm capabilities"""
        return f"""You are THOR, an advanced AI development assistant with powerful capabilities including:

CORE CAPABILITIES:
- File system operations (read/write/create/search)
- Command execution with safety checks
- Advanced code analysis and best practices enforcement
- Multi-agent swarm orchestration via Argus integration
- Memory management (chat history + artifacts)
- Cost optimization and budget management

SWARM CAPABILITIES:
- Deploy specialized agents: legal, business, financial, science, healthcare
- Orchestrate multi-agent collaboration for complex tasks
- Coordinate agent swarms for comprehensive analysis
- Manage agent lifecycle and resource allocation

OPERATIONAL GUIDELINES:
- Always USE TOOLS to perform actions, don't just describe
- Show thinking indicator during processing
- Maintain conversation context and learn from user patterns
- Follow software development best practices
- Optimize for cost efficiency (target: $5/month budget)
- Provide comprehensive error handling and logging

ENHANCED FEATURES:
- Kill switch capability for long-running operations
- Asynchronous task support for parallel processing
- Memory persistence across sessions
- Intelligent model selection based on task complexity
- Real-time cost tracking and optimization

Current session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Daily budget used: ${self.model_selector.daily_usage['cost']:.4f} / ${self.config_manager.config.max_daily_spend:.2f}
Swarm system: {'Enabled' if self.config_manager.config.enable_swarm else 'Disabled'}

IMPORTANT: When asked to perform an action, USE THE TOOLS to actually do it. Be thorough, explain your actions, and provide complete solutions."""
    
    def _signal_handler(self, signum, frame):
        """Handle graceful shutdown"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.kill_flag.set()
        asyncio.create_task(self._shutdown())
    
    async def _shutdown(self):
        """Graceful shutdown procedure"""
        try:
            # Shutdown swarm
            if self.swarm_manager.orchestrator:
                await self.swarm_manager.orchestrator.shutdown_swarm()
            
            # Save memory
            await self.memory_manager.save_all()
            
            # Save configuration
            self.config_manager.save_config()
            
            self.logger.info("Graceful shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
        finally:
            sys.exit(0)
    
    def start_thinking_indicator(self):
        """Start thinking indicator"""
        self.thinking_indicator = True
        
        def spinner():
            chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
            i = 0
            while self.thinking_indicator:
                print(f"\r🤖 THOR is thinking... {chars[i % len(chars)]}", end="", flush=True)
                time.sleep(0.1)
                i += 1
            print("\r" + " " * 50 + "\r", end="", flush=True)
        
        threading.Thread(target=spinner, daemon=True).start()
    
    def stop_thinking_indicator(self):
        """Stop thinking indicator"""
        self.thinking_indicator = False
    
    async def initialize(self):
        """Initialize THOR with all subsystems"""
        self.logger.info("Initializing THOR...")
        
        # Initialize swarm if enabled
        if self.config_manager.config.enable_swarm:
            await self.swarm_manager.initialize_swarm()
        
        # Load memory
        await self.memory_manager.load_memory()
        
        self.logger.info("THOR initialization complete")
    
    async def chat(self, message: str, session_id: str = "default") -> str:
        """Enhanced chat with memory and swarm capabilities"""
        try:
            self.start_thinking_indicator()
            
            # Check for kill signal
            if self.kill_flag.is_set():
                return "🛑 Operation cancelled by user"
            
            # Task classification for model selection
            task_type = self._classify_task(message)
            model_name, model_config = self.model_selector.choose_model(task_type)
            
            # Get conversation history
            history = await self.memory_manager.get_conversation_history(session_id)
            
            # Check if swarm assistance is needed
            swarm_agents = await self.swarm_manager.get_swarm_recommendations(message)
            
            # Prepare messages
            messages = history + [{"role": "user", "content": message}]
            
            # Make API call
            response = await self._make_api_call(messages, model_config)
            
            # Update memory
            await self.memory_manager.add_to_conversation(session_id, message, response)
            
            # Update cost tracking
            estimated_cost = self.model_selector.estimate_cost(
                len(str(messages)), len(response), model_name
            )
            self.model_selector.update_usage(estimated_cost)
            
            self.stop_thinking_indicator()
            return response
            
        except Exception as e:
            self.stop_thinking_indicator()
            self.logger.error(f"Chat error: {e}")
            return f"❌ Error: {str(e)}"
    
    def _classify_task(self, message: str) -> str:
        """Classify task for optimal model selection"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["code", "debug", "implement", "fix", "program"]):
            return "coding"
        elif any(word in message_lower for word in ["architect", "design", "security", "audit"]):
            return "architecture"
        elif any(word in message_lower for word in ["quick", "simple", "brief"]):
            return "simple_query"
        else:
            return "general"
    
    async def _make_api_call(self, messages: List[Dict], model_config) -> str:
        """Make API call with tool support"""
        try:
            # Prepare tool definitions
            tool_definitions = [
                {
                    "name": "read_file",
                    "description": "Read contents of a file",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to the file to read"}
                        },
                        "required": ["file_path"]
                    }
                },
                {
                    "name": "write_file",
                    "description": "Write content to a file",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to the file to write"},
                            "content": {"type": "string", "description": "Content to write to the file"}
                        },
                        "required": ["file_path", "content"]
                    }
                },
                {
                    "name": "orchestrate_swarm",
                    "description": "Orchestrate multiple AI agents for complex tasks",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "task": {"type": "string", "description": "Task description"},
                            "agents": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of agent types (legal, business, financial, science, healthcare)"
                            }
                        },
                        "required": ["task", "agents"]
                    }
                },
                {
                    "name": "cost_check",
                    "description": "Check current API usage and costs",
                    "input_schema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            ]
            
            response = await self.client.messages.create(
                model=model_config.name,
                max_tokens=model_config.max_tokens,
                system=self.system_prompt,
                messages=messages,
                tools=tool_definitions
            )
            
            # Handle tool calls
            if response.stop_reason == "tool_use":
                return await self._handle_tool_calls(response)
            
            return response.content[0].text if response.content else "No response"
            
        except Exception as e:
            self.logger.error(f"API call error: {e}")
            raise
    
    async def _handle_tool_calls(self, response) -> str:
        """Handle tool calls from Claude"""
        results = []
        
        for content_block in response.content:
            if content_block.type == "tool_use":
                tool_name = content_block.name
                tool_input = content_block.input
                
                if tool_name in self.tools:
                    try:
                        if asyncio.iscoroutinefunction(self.tools[tool_name]):
                            result = await self.tools[tool_name](**tool_input)
                        else:
                            result = self.tools[tool_name](**tool_input)
                        results.append(f"Tool {tool_name}: {result}")
                    except Exception as e:
                        results.append(f"Tool {tool_name} error: {str(e)}")
                else:
                    results.append(f"Unknown tool: {tool_name}")
        
        return "\n".join(results)
    
    # Tool implementations
    async def _tool_orchestrate_swarm(self, task: str, agents: List[str]) -> str:
        """Orchestrate swarm for complex tasks"""
        try:
            swarm_id = await self.swarm_manager.create_specialized_swarm("general", agents)
            result = await self.swarm_manager.execute_swarm_task(swarm_id, task)
            return f"Swarm orchestration completed: {json.dumps(result, indent=2)}"
        except Exception as e:
            return f"Swarm orchestration failed: {str(e)}"
    
    async def _tool_deploy_agent(self, agent_type: str, config: Dict = None) -> str:
        """Deploy a specialized agent"""
        try:
            config = config or {}
            success = await self.swarm_manager.orchestrator.deploy_agent(agent_type, config)
            return f"Agent {agent_type} deployment: {'Success' if success else 'Failed'}"
        except Exception as e:
            return f"Agent deployment failed: {str(e)}"
    
    async def _tool_get_swarm_status(self) -> str:
        """Get current swarm status"""
        try:
            status = await self.swarm_manager.orchestrator.get_swarm_status()
            return json.dumps(status, indent=2)
        except Exception as e:
            return f"Status check failed: {str(e)}"
    
    def _tool_cost_check(self) -> str:
        """Check current costs and usage"""
        usage = self.model_selector.daily_usage
        return f"""💰 Cost Report:
Daily Usage: ${usage['cost']:.4f} / ${self.config_manager.config.max_daily_spend:.2f}
Requests Today: {usage['requests']}
Budget Remaining: ${self.config_manager.config.max_daily_spend - usage['cost']:.4f}
Date: {usage['date']}"""
    
    # File operation tools (existing implementations)
    def _tool_read_file(self, file_path: str) -> str:
        """Read file contents"""
        return self.file_ops.read_file(file_path)
    
    def _tool_write_file(self, file_path: str, content: str) -> str:
        """Write file contents"""
        return self.file_ops.write_file(file_path, content)
    
    def _tool_list_files(self, directory: str = ".") -> str:
        """List files in directory"""
        return self.file_ops.list_files(directory)
    
    def _tool_create_directory(self, directory_path: str) -> str:
        """Create directory"""
        return self.file_ops.create_directory(directory_path)
    
    def _tool_run_command(self, command: str) -> str:
        """Run system command"""
        return self.file_ops.run_command(command)
    
    def _tool_search_files(self, pattern: str, directory: str = ".") -> str:
        """Search files for pattern"""
        return self.file_ops.search_files(pattern, directory)
    
    def _tool_analyze_code(self, file_path: str) -> str:
        """Analyze code file"""
        return self.file_ops.analyze_code(file_path)
    
    async def _tool_get_memory(self, session_id: str = "default") -> str:
        """Get memory for session"""
        memory = await self.memory_manager.get_conversation_history(session_id)
        return json.dumps(memory[-10:], indent=2)  # Last 10 messages
    
    async def _tool_save_artifact(self, name: str, content: str, category: str = "general") -> str:
        """Save artifact to memory"""
        await self.memory_manager.save_artifact(name, content, category)
        return f"Artifact '{name}' saved successfully"