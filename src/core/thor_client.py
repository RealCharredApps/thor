# thor/src/core/thor_client.py
import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor
import anthropic
import subprocess
import re
import ast
import yaml
from .swarm_manager import SwarmManager
from ..agents.argus_orchestrator import ArgusOrchestrator
from ..utils.model_selector import ModelSelector
from ..utils.conversation_memory import ConversationMemory
from ..utils.artifact_manager import ArtifactManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('thor/logs/thor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ThorConfig:
    """Configuration for THOR client"""
    anthropic_api_key: str
    default_model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    temperature: float = 0.7
    conversation_memory_limit: int = 50
    enable_swarm: bool = True
    swarm_timeout: int = 300
    auto_save_conversations: bool = True
    kill_switch_enabled: bool = True
    parallel_sessions: bool = True
    session_id: Optional[str] = None
    
class ThorClient:
    """Advanced AI Development Assistant with Swarm Capabilities"""
    
    def __init__(self, config: ThorConfig):
        self.config = config
        self.anthropic_client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        self.session_id = config.session_id or self._generate_session_id()
        self.kill_switch = threading.Event()
        self.is_running = False
        
        # Initialize managers
        self.model_selector = ModelSelector()
        self.conversation_memory = ConversationMemory(
            session_id=self.session_id,
            limit=config.conversation_memory_limit
        )
        self.artifact_manager = ArtifactManager()
        
        # Initialize swarm components
        if config.enable_swarm:
            self.swarm_manager = SwarmManager()
            self.argus_orchestrator = ArgusOrchestrator()
        else:
            self.swarm_manager = None
            self.argus_orchestrator = None
            
        # Tool registry
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
            'manage_conversation': self._tool_manage_conversation,
            'create_artifact': self._tool_create_artifact,
            'get_artifact': self._tool_get_artifact,
            'kill_switch': self._tool_kill_switch,
            'parallel_execute': self._tool_parallel_execute,
        }
        
        # System prompts
        self.system_prompt = self._build_system_prompt()
        
        logger.info(f"THOR Client initialized with session: {self.session_id}")
        
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"thor_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
    
    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt"""
        prompt = """You are THOR, an advanced AI development assistant with access to powerful tools and swarm capabilities.

Core Capabilities:
- File system operations (read/write/create/analyze)
- Command execution with error handling
- Code analysis and best practices enforcement
- Swarm orchestration for complex tasks
- Multi-agent coordination via Argus system
- Conversation and artifact memory management
- Parallel task execution
- Kill switch for emergency stops

Tool Usage Guidelines:
1. Always USE TOOLS to perform actions, don't just describe
2. Check for kill switch before long operations
3. Use appropriate model for task complexity
4. Maintain conversation context and artifacts
5. Follow security best practices
6. Provide detailed explanations of actions

Swarm Integration:
- Use orchestrate_swarm for complex multi-domain tasks
- Deploy specialized agents for specific domains (legal, business, science, etc.)
- Coordinate parallel execution when beneficial
- Monitor swarm status and handle failures gracefully

Model Selection Strategy:
- Quick fixes, coding, debugging: Sonnet-4
- Architecture, security audits, complex analysis: Opus-4
- Default to Sonnet-4 for efficiency

Security & Best Practices:
- Never expose API keys or secrets
- Validate all inputs and outputs
- Use proper error handling
- Log all significant operations
- Respect rate limits and costs

Be thorough, efficient, and always explain your reasoning."""
        
        return prompt
    
    async def process_message(self, message: str, task_type: str = "general") -> Dict[str, Any]:
        """Process user message with intelligent routing"""
        if self.kill_switch.is_set():
            return {"error": "Kill switch activated", "status": "stopped"}
            
        self.is_running = True
        start_time = datetime.now()
        
        try:
            # Select appropriate model
            model = self.model_selector.choose_model(task_type)
            logger.info(f"Selected model: {model} for task: {task_type}")
            
            # Store conversation
            self.conversation_memory.add_message("user", message)
            
            # Get conversation context
            context = self.conversation_memory.get_context()
            
            # Prepare messages for API
            messages = [
                {"role": "system", "content": self.system_prompt},
                *context,
                {"role": "user", "content": message}
            ]
            
            # Process with selected model
            response = await self._process_with_model(messages, model)
            
            # Store response
            self.conversation_memory.add_message("assistant", response.get("content", ""))
            
            # Calculate usage
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "response": response,
                "model_used": model,
                "processing_time": processing_time,
                "session_id": self.session_id,
                "status": "completed"
            }
            
            # Auto-save if enabled
            if self.config.auto_save_conversations:
                self.conversation_memory.save_to_file()
                
            return result
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "error": str(e),
                "status": "error",
                "session_id": self.session_id
            }
        finally:
            self.is_running = False
    
    async def _process_with_model(self, messages: List[Dict], model: str) -> Dict[str, Any]:
        """Process messages with specified model"""
        try:
            # Check for kill switch before API call
            if self.kill_switch.is_set():
                return {"error": "Kill switch activated", "content": ""}
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.anthropic_client.messages.create(
                    model=model,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    messages=messages,
                    tools=self._get_tool_definitions()
                )
            )
            
            # Handle tool calls
            if response.stop_reason == "tool_use":
                return await self._handle_tool_calls(response)
            
            return {
                "content": response.content[0].text if response.content else "",
                "usage": response.usage.__dict__ if hasattr(response, 'usage') else {},
                "stop_reason": response.stop_reason
            }
            
        except Exception as e:
            logger.error(f"Model processing error: {str(e)}")
            raise
    
    async def _handle_tool_calls(self, response) -> Dict[str, Any]:
        """Handle tool calls from model response"""
        results = []
        
        for content_block in response.content:
            if content_block.type == "tool_use":
                tool_name = content_block.name
                tool_input = content_block.input
                
                # Check kill switch before tool execution
                if self.kill_switch.is_set():
                    return {"error": "Kill switch activated during tool execution", "content": ""}
                
                if tool_name in self.tools:
                    try:
                        result = await self.tools[tool_name](tool_input)
                        results.append({
                            "tool": tool_name,
                            "input": tool_input,
                            "output": result
                        })
                    except Exception as e:
                        logger.error(f"Tool execution error: {tool_name} - {str(e)}")
                        results.append({
                            "tool": tool_name,
                            "input": tool_input,
                            "error": str(e)
                        })
                else:
                    results.append({
                        "tool": tool_name,
                        "input": tool_input,
                        "error": f"Unknown tool: {tool_name}"
                    })
        
        return {
            "content": "Tool execution completed",
            "tool_results": results,
            "stop_reason": "tool_use"
        }
    
    def _get_tool_definitions(self) -> List[Dict]:
        """Get tool definitions for API"""
        return [
            {
                "name": "read_file",
                "description": "Read content from a file",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to file"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "write_file",
                "description": "Write content to a file",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to file"},
                        "content": {"type": "string", "description": "Content to write"}
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "orchestrate_swarm",
                "description": "Orchestrate multiple AI agents for complex tasks",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string", "description": "Task description"},
                        "agents": {"type": "array", "items": {"type": "string"}, "description": "Agent types to use"},
                        "coordination_mode": {"type": "string", "enum": ["sequential", "parallel", "hierarchical"], "default": "sequential"}
                    },
                    "required": ["task", "agents"]
                }
            },
            {
                "name": "kill_switch",
                "description": "Emergency stop for all operations",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "reason": {"type": "string", "description": "Reason for emergency stop"}
                    }
                }
            }
            # Add more tool definitions...
        ]
    
    # Tool implementations
    async def _tool_read_file(self, params: Dict) -> Dict[str, Any]:
        """Read file tool"""
        try:
            path = params.get("path", "")
            if not path:
                return {"error": "Path parameter required"}
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "path": path,
                "size": len(content)
            }
        except Exception as e:
            return {"error": str(e), "path": path}
    
    async def _tool_write_file(self, params: Dict) -> Dict[str, Any]:
        """Write file tool"""
        try:
            path = params.get("path", "")
            content = params.get("content", "")
            
            if not path:
                return {"error": "Path parameter required"}
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "path": path,
                "bytes_written": len(content.encode('utf-8'))
            }
        except Exception as e:
            return {"error": str(e), "path": path}
    
    async def _tool_orchestrate_swarm(self, params: Dict) -> Dict[str, Any]:
        """Orchestrate swarm tool"""
        if not self.swarm_manager:
            return {"error": "Swarm not enabled"}
        
        try:
            task = params.get("task", "")
            agents = params.get("agents", [])
            coordination_mode = params.get("coordination_mode", "sequential")
            
            if not task or not agents:
                return {"error": "Task and agents parameters required"}
            
            result = await self.swarm_manager.orchestrate_task(
                task=task,
                agents=agents,
                mode=coordination_mode
            )
            
            return {
                "success": True,
                "task": task,
                "agents": agents,
                "result": result
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _tool_kill_switch(self, params: Dict) -> Dict[str, Any]:
        """Kill switch tool"""
        reason = params.get("reason", "Emergency stop requested")
        self.kill_switch.set()
        logger.warning(f"Kill switch activated: {reason}")
        
        return {
            "success": True,
            "reason": reason,
            "message": "All operations stopped"
        }
    
    def reset_kill_switch(self):
        """Reset kill switch"""
        self.kill_switch.clear()
        logger.info("Kill switch reset")
    
    async def _tool_parallel_execute(self, params: Dict) -> Dict[str, Any]:
        """Execute multiple tasks in parallel"""
        tasks = params.get("tasks", [])
        max_workers = params.get("max_workers", 3)
        
        if not tasks:
            return {"error": "No tasks provided"}
        
        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for task in tasks:
                    future = executor.submit(self._execute_single_task, task)
                    futures.append(future)
                
                results = []
                for future in futures:
                    if self.kill_switch.is_set():
                        break
                    result = future.result()
                    results.append(result)
                
                return {
                    "success": True,
                    "results": results,
                    "completed": len(results)
                }
        except Exception as e:
            return {"error": str(e)}
    
    def _execute_single_task(self, task: Dict) -> Dict[str, Any]:
        """Execute a single task"""
        # Implementation for single task execution
        pass
    
    # Additional tool implementations...
    async def _tool_list_files(self, params: Dict) -> Dict[str, Any]:
        """List files tool"""
        try:
            path = params.get("path", ".")
            pattern = params.get("pattern", "*")
            
            files = []
            for file_path in Path(path).glob(pattern):
                files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "is_dir": file_path.is_dir(),
                    "size": file_path.stat().st_size if file_path.is_file() else 0
                })
            
            return {
                "success": True,
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _tool_create_directory(self, params: Dict) -> Dict[str, Any]:
        """Create directory tool"""
        try:
            path = params.get("path", "")
            if not path:
                return {"error": "Path parameter required"}
            
            os.makedirs(path, exist_ok=True)
            return {
                "success": True,
                "path": path,
                "created": True
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _tool_run_command(self, params: Dict) -> Dict[str, Any]:
        """Run command tool"""
        try:
            command = params.get("command", "")
            if not command:
                return {"error": "Command parameter required"}
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": True,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _tool_search_files(self, params: Dict) -> Dict[str, Any]:
        """Search files tool"""
        try:
            path = params.get("path", ".")
            pattern = params.get("pattern", "")
            content_search = params.get("content_search", "")
            
            results = []
            for file_path in Path(path).rglob("*"):
                if file_path.is_file():
                    if pattern and pattern not in file_path.name:
                        continue
                    
                    if content_search:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if content_search in content:
                                    results.append({
                                        "path": str(file_path),
                                        "matches": content.count(content_search)
                                    })
                        except:
                            continue
                    else:
                        results.append({"path": str(file_path)})
            
            return {
                "success": True,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _tool_analyze_code(self, params: Dict) -> Dict[str, Any]:
        """Analyze code tool"""
        try:
            path = params.get("path", "")
            if not path:
                return {"error": "Path parameter required"}
            
            with open(path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Basic code analysis
            analysis = {
                "lines": len(code.splitlines()),
                "characters": len(code),
                "functions": len(re.findall(r'def\s+\w+', code)),
                "classes": len(re.findall(r'class\s+\w+', code)),
                "imports": len(re.findall(r'^import\s+|^from\s+', code, re.MULTILINE)),
                "comments": len(re.findall(r'#.*|""".*?"""', code, re.DOTALL)),
                "complexity": "medium"  # Simplified
            }
            
            return {
                "success": True,
                "path": path,
                "analysis": analysis
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _tool_deploy_agent(self, params: Dict) -> Dict[str, Any]:
        """Deploy agent tool"""
        if not self.swarm_manager:
            return {"error": "Swarm not enabled"}
        
        try:
            agent_type = params.get("agent_type", "")
            config = params.get("config", {})
            
            if not agent_type:
                return {"error": "Agent type required"}
            
            agent_id = await self.swarm_manager.deploy_agent(agent_type, config)
            
            return {
                "success": True,
                "agent_id": agent_id,
                "agent_type": agent_type,
                "status": "deployed"
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _tool_get_swarm_status(self, params: Dict) -> Dict[str, Any]:
        """Get swarm status tool"""
        if not self.swarm_manager:
            return {"error": "Swarm not enabled"}
        
        try:
            status = await self.swarm_manager.get_status()
            return {
                "success": True,
                "status": status
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _tool_manage_conversation(self, params: Dict) -> Dict[str, Any]:
        """Manage conversation tool"""
        try:
            action = params.get("action", "")
            
            if action == "save":
                filepath = self.conversation_memory.save_to_file()
                return {"success": True, "filepath": filepath}
            elif action == "load":
                filepath = params.get("filepath", "")
                self.conversation_memory.load_from_file(filepath)
                return {"success": True, "loaded": filepath}
            elif action == "clear":
                self.conversation_memory.clear()
                return {"success": True, "cleared": True}
            elif action == "summary":
                summary = self.conversation_memory.get_summary()
                return {"success": True, "summary": summary}
            else:
                return {"error": "Unknown action"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _tool_create_artifact(self, params: Dict) -> Dict[str, Any]:
        """Create artifact tool"""
        try:
            name = params.get("name", "")
            content = params.get("content", "")
            artifact_type = params.get("type", "text")
            
            if not name or not content:
                return {"error": "Name and content required"}
            
            artifact_id = self.artifact_manager.create_artifact(name, content, artifact_type)
            
            return {
                "success": True,
                "artifact_id": artifact_id,
                "name": name,
                "type": artifact_type
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _tool_get_artifact(self, params: Dict) -> Dict[str, Any]:
        """Get artifact tool"""
        try:
            artifact_id = params.get("artifact_id", "")
            if not artifact_id:
                return {"error": "Artifact ID required"}
            
            artifact = self.artifact_manager.get_artifact(artifact_id)
            if not artifact:
                return {"error": "Artifact not found"}
            
            return {
                "success": True,
                "artifact": artifact
            }
        except Exception as e:
            return {"error": str(e)}
# End of ThorClient class
