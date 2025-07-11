# src/core/thor_client.py - FINAL NO-STREAMING VERSION
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
from .memory_manager import MemoryManager
from .file_operations import FileOperations

class ThorClient:
    """THOR client with reliable API calls"""
    
    def __init__(self, config_path: str = "thor_config.json"):
        self.config_manager = ConfigManager(config_path)
        self.model_selector = ModelSelector(self.config_manager)
        self.memory_manager = MemoryManager(self.config_manager)
        self.file_ops = FileOperations()
        
        if not self.config_manager.config.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Please set it in your environment.")
        
        self.client = anthropic.Anthropic(api_key=self.config_manager.config.api_key)
        self.logger = logging.getLogger(__name__)
        
        # State management
        self.kill_flag = threading.Event()
        self.thinking_indicator = False
        
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
            'get_memory': self._tool_get_memory,
            'save_artifact': self._tool_save_artifact,
            'cost_check': self._tool_cost_check,
            'swarm_status': self._tool_swarm_status
        }
    
    def _build_enhanced_system_prompt(self) -> str:
        """Build comprehensive system prompt"""
        return f"""You are THOR, an advanced AI development assistant with powerful capabilities.

CORE CAPABILITIES:
- File system operations (read/write/create/search)
- Command execution with safety checks
- Advanced code analysis and best practices enforcement
- Memory management (chat history + artifacts)
- Cost optimization and budget management

SWARM STATUS:
- Argus swarm integration: Not currently active
- Available when Argus MCP servers are running

OPERATIONAL GUIDELINES:
- Always USE TOOLS to perform actions, don't just describe
- Provide clear, actionable responses
- Follow software development best practices
- Be helpful and thorough

Current session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Daily budget used: ${self.model_selector.daily_usage['cost']:.4f} / ${self.config_manager.config.max_daily_spend:.2f}

IMPORTANT: When asked to perform an action, USE THE TOOLS to actually do it."""
    
    def start_thinking_indicator(self):
        """Start thinking indicator"""
        self.thinking_indicator = True
        
        def spinner():
            chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
            i = 0
            while self.thinking_indicator and not self.kill_flag.is_set():
                print(f"\r🤖 THOR is thinking... {chars[i % len(chars)]}", end="", flush=True)
                time.sleep(0.1)
                i += 1
            print("\r" + " " * 50 + "\r", end="", flush=True)
        
        threading.Thread(target=spinner, daemon=True).start()
    
    def stop_thinking_indicator(self):
        """Stop thinking indicator"""
        self.thinking_indicator = False
        time.sleep(0.1)
    
    async def initialize(self):
        """Initialize THOR with all subsystems"""
        self.logger.info("Initializing THOR...")
        await self.memory_manager.load_memory()
        self.logger.info("THOR initialization complete")
    
    async def chat(self, message: str, session_id: str = "default") -> str:
        """Enhanced chat with proper API handling"""
        try:
            self.start_thinking_indicator()
            
            # Check for kill signal
            if self.kill_flag.is_set():
                self.stop_thinking_indicator()
                return "🛑 Operation cancelled by user"
            
            # Task classification for model selection
            task_type = self._classify_task(message)
            model_name, model_config = self.model_selector.choose_model(task_type)
            
            # Get conversation history (API compatible format)
            history = await self.memory_manager.get_conversation_history(session_id)
            recent_history = history[-8:] if len(history) > 8 else history
            
            # Prepare messages for API
            messages = recent_history + [{"role": "user", "content": message}]
            
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
        """Make synchronous API call with tools"""
        try:
            # Tool definitions
            tools = [
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
                    "name": "list_files",
                    "description": "List files in a directory",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "directory": {"type": "string", "description": "Directory path", "default": "."}
                        }
                    }
                },
                {
                    "name": "run_command",
                    "description": "Run a system command",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "Command to run"}
                        },
                        "required": ["command"]
                    }
                }
            ]
            
            # Make synchronous API call
            response = self.client.messages.create(
                model=model_config.name,
                max_tokens=4000,
                system=self.system_prompt,
                messages=messages,
                tools=tools
            )
            
            # Process response
            if response.stop_reason == "tool_use":
                return await self._handle_tool_calls(response)
            
            return response.content[0].text if response.content else "No response received"
            
        except Exception as e:
            self.logger.error(f"API call error: {e}")
            return f"❌ API Error: {str(e)}"
    
    async def _handle_tool_calls(self, response) -> str:
        """Handle tool calls from API response"""
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
                        results.append(f"🔧 {tool_name}: {result}")
                    except Exception as e:
                        results.append(f"❌ {tool_name} error: {str(e)}")
                else:
                    results.append(f"❌ Unknown tool: {tool_name}")
            elif content_block.type == "text":
                results.append(content_block.text)
        
        return "\n".join(results)
    
    # Tool implementations
    def _tool_read_file(self, file_path: str) -> str:
        return self.file_ops.read_file(file_path)
    
    def _tool_write_file(self, file_path: str, content: str) -> str:
        return self.file_ops.write_file(file_path, content)
    
    def _tool_list_files(self, directory: str = ".") -> str:
        return self.file_ops.list_files(directory)
    
    def _tool_create_directory(self, directory_path: str) -> str:
        return self.file_ops.create_directory(directory_path)
    
    def _tool_run_command(self, command: str) -> str:
        return self.file_ops.run_command(command)
    
    def _tool_search_files(self, pattern: str, directory: str = ".") -> str:
        return self.file_ops.search_files(pattern, directory)
    
    def _tool_analyze_code(self, file_path: str) -> str:
        return self.file_ops.analyze_code(file_path)
    
    def _tool_cost_check(self) -> str:
        usage = self.model_selector.daily_usage
        return f"""💰 Cost Report:
Daily Usage: ${usage['cost']:.4f} / ${self.config_manager.config.max_daily_spend:.2f}
Requests Today: {usage['requests']}
Budget Remaining: ${self.config_manager.config.max_daily_spend - usage['cost']:.4f}
Date: {usage['date']}"""
    
    def _tool_swarm_status(self) -> str:
        argus_path = self.config_manager.config.argus_path
        if not argus_path:
            return "❌ Argus swarm not configured. Set ARGUS_PATH environment variable."
        
        from pathlib import Path
        argus_dir = Path(argus_path)
        
        if not argus_dir.exists():
            return f"❌ Argus directory not found: {argus_path}"
        
        # Check for MCP servers
        mcp_servers = []
        for mcp_file in argus_dir.glob("*-mcp-server.js"):
            mcp_servers.append(mcp_file.name)
        
        if not mcp_servers:
            return f"❌ No MCP servers found in {argus_path}"
        
        return f"""🤖 Argus Swarm Status:
Path: {argus_path}
Available MCP Servers: {len(mcp_servers)}
- {chr(10).join(mcp_servers)}

Status: ⚠️ Not currently running
To activate: Run MCP servers and orchestrator"""
    
    async def _tool_get_memory(self, session_id: str = "default") -> str:
        memory = await self.memory_manager.get_conversation_history(session_id)
        return json.dumps(memory[-3:], indent=2)
    
    async def _tool_save_artifact(self, name: str, content: str, category: str = "general") -> str:
        await self.memory_manager.save_artifact(name, content, category)
        return f"Artifact '{name}' saved successfully"