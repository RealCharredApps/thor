## Fixed THOR Client

# thor/src/core/thor_client.py (Fixed Version)
import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor
import signal
import sys
import traceback

try:
    import anthropic
except ImportError:
    print("❌ anthropic package not found. Install with: pip install anthropic")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("❌ PyYAML not found. Install with: pip install pyyaml")
    sys.exit(1)

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
    monthly_budget: float = 5.0
    debug_mode: bool = False

class ThorClient:
    """Advanced AI Development Assistant with Swarm Capabilities"""
    
    def __init__(self, config: ThorConfig):
        self.config = config
        self.session_id = config.session_id or self._generate_session_id()
        self.kill_switch = threading.Event()
        self.is_running = False
        self.debug_mode = config.debug_mode
        
        # Initialize Anthropic client
        try:
            self.anthropic_client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise
        
        # Initialize directories
        self._setup_directories()
        
        # Initialize managers (with safe imports)
        self._initialize_managers()
        
        # Tool registry
        self.tools = {
            'read_file': self._tool_read_file,
            'write_file': self._tool_write_file,
            'list_files': self._tool_list_files,
            'create_directory': self._tool_create_directory,
            'run_command': self._tool_run_command,
            'search_files': self._tool_search_files,
            'analyze_code': self._tool_analyze_code,
            'kill_switch': self._tool_kill_switch,
            'manage_conversation': self._tool_manage_conversation,
            'create_artifact': self._tool_create_artifact,
            'get_artifact': self._tool_get_artifact,
        }
        
        # Add swarm tools if enabled
        if config.enable_swarm:
            self.tools.update({
                'orchestrate_swarm': self._tool_orchestrate_swarm,
                'deploy_agent': self._tool_deploy_agent,
                'get_swarm_status': self._tool_get_swarm_status,
            })
        
        # System prompt
        self.system_prompt = self._build_system_prompt()
        
        logger.info(f"THOR Client initialized with session: {self.session_id}")
    
    def _setup_directories(self):
        """Setup required directories"""
        directories = ['thor/logs', 'thor/memory', 'thor/artifacts']
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _initialize_managers(self):
        """Initialize managers with safe imports"""
        # Basic managers (always available)
        self.model_selector = ModelSelector()
        self.conversation_memory = ConversationMemory(
            session_id=self.session_id,
            limit=self.config.conversation_memory_limit
        )
        self.artifact_manager = ArtifactManager()
        
        # Swarm managers (optional)
        if self.config.enable_swarm:
            try:
                self.swarm_manager = SwarmManager()
                self.argus_orchestrator = ArgusOrchestrator()
            except Exception as e:
                logger.warning(f"Failed to initialize swarm components: {e}")
                self.swarm_manager = None
                self.argus_orchestrator = None
                self.config.enable_swarm = False
        else:
            self.swarm_manager = None
            self.argus_orchestrator = None
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"thor_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
    
    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt"""
        return """You are THOR, an advanced AI development assistant with powerful capabilities.

Core Functions:
- File system operations (read, write, analyze, manage)
- Code analysis and optimization
- Command execution with error handling
- Conversation memory and context management
- Artifact creation and management

When given a task:
1. USE THE TOOLS to perform actions - don't just describe
2. Provide clear explanations of what you're doing
3. Handle errors gracefully and suggest solutions
4. Maintain conversation context and learn from interactions

Be helpful, thorough, and security-conscious in all operations."""
    
    async def process_message(self, message: str, task_type: str = "general") -> Dict[str, Any]:
        """Process user message with intelligent routing"""
        if self.kill_switch.is_set():
            return {"error": "Kill switch activated", "status": "stopped"}
        
        self.is_running = True
        start_time = datetime.now()
        
        try:
            # Select appropriate model
            model = self.model_selector.choose_model(task_type)
            if self.debug_mode:
                logger.info(f"Selected model: {model} for task: {task_type}")
            
            # Store conversation
            self.conversation_memory.add_message("user", message)
            
            # Get conversation context
            context = self.conversation_memory.get_context()
            
            # Prepare messages for API
            messages = [
                {"role": "system", "content": self.system_prompt},
                *context[-10:],  # Last 10 messages for context
                {"role": "user", "content": message}
            ]
            
            # Process with selected model
            response = await self._process_with_model(messages, model)
            
            # Store response
            if response.get("content"):
                self.conversation_memory.add_message("assistant", response["content"])
            
            # Calculate metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Track usage
            if "usage" in response:
                usage = response["usage"]
                total_tokens = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                self.model_selector.track_usage(model, total_tokens)
            
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
            if self.debug_mode:
                logger.error(traceback.format_exc())
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
            # Check for kill switch
            if self.kill_switch.is_set():
                return {"error": "Kill switch activated", "content": ""}
            
            # Make API call
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.anthropic_client.messages.create(
                    model=model,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    messages=messages,
                    tools=self._get_tool_definitions() if self.tools else None
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
                
                # Check kill switch
                if self.kill_switch.is_set():
                    return {"error": "Kill switch activated during tool execution"}
                
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
                "name": "list_files",
                "description": "List files in a directory",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path", "default": "."},
                        "pattern": {"type": "string", "description": "File pattern", "default": "*"}
                    }
                }
            },
            {
                "name": "run_command",
                "description": "Execute a system command",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Command to execute"}
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "analyze_code",
                "description": "Analyze code for quality, security, and optimization",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to code file"}
                    },
                    "required": ["path"]
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
        ]
    
    # Tool implementations
    async def _tool_read_file(self, params: Dict) -> Dict[str, Any]:
        """Read file tool"""
        try:
            path = params.get("path", "")
            if not path:
                return {"error": "Path parameter required"}
            
            # Security check
            if not self._is_safe_path(path):
                return {"error": "Access denied: unsafe path"}
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "path": path,
                "size": len(content)
            }
        except FileNotFoundError:
            return {"error": f"File not found: {path}"}
        except PermissionError:
            return {"error": f"Permission denied: {path}"}
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}
    
    async def _tool_write_file(self, params: Dict) -> Dict[str, Any]:
        """Write file tool"""
        try:
            path = params.get("path", "")
            content = params.get("content", "")
            
            if not path:
                return {"error": "Path parameter required"}
            
            # Security check
            if not self._is_safe_path(path):
                return {"error": "Access denied: unsafe path"}
            
            # Create directory if needed
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "path": path,
                "bytes_written": len(content.encode('utf-8'))
            }
        except PermissionError:
            return {"error": f"Permission denied: {path}"}
        except Exception as e:
            return {"error": f"Failed to write file: {str(e)}"}
    
    async def _tool_list_files(self, params: Dict) -> Dict[str, Any]:
        """List files tool"""
        try:
            path = params.get("path", ".")
            pattern = params.get("pattern", "*")
            
            if not self._is_safe_path(path):
                return {"error": "Access denied: unsafe path"}
            
            files = []
            path_obj = Path(path)
            
            if not path_obj.exists():
                return {"error": f"Path does not exist: {path}"}
            
            for file_path in path_obj.glob(pattern):
                try:
                    stat = file_path.stat()
                    files.append({
                        "name": file_path.name,
                        "path": str(file_path),
                        "is_dir": file_path.is_dir(),
                        "size": stat.st_size if file_path.is_file() else 0,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except (OSError, PermissionError):
                    continue
            
            return {
                "success": True,
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {"error": f"Failed to list files: {str(e)}"}
    
    async def _tool_create_directory(self, params: Dict) -> Dict[str, Any]:
        """Create directory tool"""
        try:
            path = params.get("path", "")
            if not path:
                return {"error": "Path parameter required"}
            
            if not self._is_safe_path(path):
                return {"error": "Access denied: unsafe path"}
            
            os.makedirs(path, exist_ok=True)
            return {
                "success": True,
                "path": path,
                "created": True
            }
        except Exception as e:
            return {"error": f"Failed to create directory: {str(e)}"}
    
    async def _tool_run_command(self, params: Dict) -> Dict[str, Any]:
        """Run command tool"""
        try:
            command = params.get("command", "")
            if not command:
                return {"error": "Command parameter required"}
            
            # Security check - basic command validation
            if not self._is_safe_command(command):
                return {"error": "Command not allowed for security reasons"}
            
            import subprocess
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            return {
                "success": True,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}
        except Exception as e:
            return {"error": f"Failed to run command: {str(e)}"}
    
    async def _tool_search_files(self, params: Dict) -> Dict[str, Any]:
        """Search files tool"""
        try:
            path = params.get("path", ".")
            pattern = params.get("pattern", "")
            content_search = params.get("content_search", "")
            
            if not self._is_safe_path(path):
                return {"error": "Access denied: unsafe path"}
            
            results = []
            search_path = Path(path)
            
            if not search_path.exists():
                return {"error": f"Path does not exist: {path}"}
            
            for file_path in search_path.rglob("*"):
                if not file_path.is_file():
                    continue
                
                try:
                    # Check filename pattern
                    if pattern and pattern not in file_path.name:
                        continue
                    
                    # Check content if specified
                    if content_search:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if content_search.lower() in content.lower():
                                    results.append({
                                        "path": str(file_path),
                                        "matches": content.lower().count(content_search.lower())
                                    })
                        except (UnicodeDecodeError, PermissionError):
                            continue
                    else:
                        results.append({"path": str(file_path)})
                        
                except (OSError, PermissionError):
                    continue
            
            return {
                "success": True,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {"error": f"Failed to search files: {str(e)}"}
    
    async def _tool_analyze_code(self, params: Dict) -> Dict[str, Any]:
        """Analyze code tool"""
        try:
            path = params.get("path", "")
            if not path:
                return {"error": "Path parameter required"}
            
            if not self._is_safe_path(path):
                return {"error": "Access denied: unsafe path"}
            
            with open(path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Basic code analysis
            import re
            analysis = {
                "lines": len(code.splitlines()),
                "characters": len(code),
                "functions": len(re.findall(r'def\s+\w+', code)),
                "classes": len(re.findall(r'class\s+\w+', code)),
                "imports": len(re.findall(r'^import\s+|^from\s+', code, re.MULTILINE)),
                "comments": len(re.findall(r'#.*|""".*?"""', code, re.DOTALL)),
                "todo_items": len(re.findall(r'#\s*TODO|#\s*FIXME|#\s*XXX', code, re.IGNORECASE)),
                "file_extension": Path(path).suffix,
                "estimated_complexity": self._estimate_complexity(code)
            }
            
            return {
                "success": True,
                "path": path,
                "analysis": analysis
            }
        except Exception as e:
            return {"error": f"Failed to analyze code: {str(e)}"}
    
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
    
    async def _tool_manage_conversation(self, params: Dict) -> Dict[str, Any]:
        """Manage conversation tool"""
        try:
            action = params.get("action", "")
            
            if action == "save":
                filepath = self.conversation_memory.save_to_file()
                return {"success": True, "filepath": filepath}
            elif action == "load":
                filepath = params.get("filepath", "")
                if not filepath:
                    return {"error": "Filepath required for load action"}
                self.conversation_memory.load_from_file(filepath)
                return {"success": True, "loaded": filepath}
            elif action == "clear":
                self.conversation_memory.clear()
                return {"success": True, "cleared": True}
            elif action == "summary":
                summary = self.conversation_memory.get_summary()
                return {"success": True, "summary": summary}
            elif action == "export":
                filepath = self.conversation_memory.export_markdown()
                return {"success": True, "exported": filepath}
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            return {"error": f"Failed to manage conversation: {str(e)}"}
    
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
            return {"error": f"Failed to create artifact: {str(e)}"}
    
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
            return {"error": f"Failed to get artifact: {str(e)}"}
    
    # Swarm tools (if enabled)
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
            return {"error": f"Failed to orchestrate swarm: {str(e)}"}
    
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
            return {"error": f"Failed to deploy agent: {str(e)}"}
    
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
            return {"error": f"Failed to get swarm status: {str(e)}"}
    
    # Security and utility methods
    def _is_safe_path(self, path: str) -> bool:
        """Check if path is safe to access"""
        try:
            # Convert to absolute path
            abs_path = os.path.abspath(path)
            
            # Check for directory traversal
            if ".." in path or path.startswith("/"):
                return False
            
            # Check for system directories
            system_dirs = ["/etc", "/proc", "/sys", "/dev", "/root"]
            for sys_dir in system_dirs:
                if abs_path.startswith(sys_dir):
                    return False
            
            return True
        except:
            return False
    
    def _is_safe_command(self, command: str) -> bool:
        """Check if command is safe to execute"""
        # Basic security - block dangerous commands
        dangerous_commands = [
            "rm -rf", "del", "format", "fdisk", "mkfs",
            "sudo", "su", "chmod 777", "chown",
            "wget", "curl", "nc", "netcat",
            "python -c", "eval", "exec"
        ]
        
        command_lower = command.lower()
        for dangerous in dangerous_commands:
            if dangerous in command_lower:
                return False
        
        return True
    
    def _estimate_complexity(self, code: str) -> str:
        """Estimate code complexity"""
        lines = len(code.splitlines())
        
        if lines < 50:
            return "low"
        elif lines < 200:
            return "medium"
        else:
            return "high"
    
    def reset_kill_switch(self):
        """Reset kill switch"""
        self.kill_switch.clear()
        logger.info("Kill switch reset")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "session_id": self.session_id,
            "model_usage": self.model_selector.get_usage_stats(),
            "conversation_stats": self.conversation_memory.get_summary(),
            "artifacts_count": len(self.artifact_manager.list_artifacts()),
            "swarm_enabled": self.config.enable_swarm,
            "kill_switch_active": self.kill_switch.is_set()
        }
    
    def shutdown(self):
        """Shutdown THOR client"""
        logger.info("Shutting down THOR client...")
        
        # Set kill switch
        self.kill_switch.set()
        
        # Save conversation
        if self.config.auto_save_conversations:
            self.conversation_memory.save_to_file()
        
        # Shutdown swarm if enabled
        if self.swarm_manager:
            self.swarm_manager.shutdown()
        
        if self.argus_orchestrator:
            self.argus_orchestrator.shutdown()
        
        logger.info("THOR client shutdown complete")

# Simple implementations for required classes
class ModelSelector:
    """Simple model selector"""
    
    def __init__(self):
        self.usage_stats = {"total_tokens": 0, "total_cost": 0.0}
    
    def choose_model(self, task_type: str) -> str:
        """Choose model based on task type"""
        if task_type in ['simple_query', 'quick_answer']:
            return "claude-3-haiku-20240307"
        elif task_type in ['architecture', 'security_audit', 'complex_analysis']:
            return "claude-3-opus-20240229"
        else:
            return "claude-3-5-sonnet-20241022"
    
    def track_usage(self, model: str, tokens: int):
        """Track usage"""
        self.usage_stats["total_tokens"] += tokens
        # Simplified cost calculation
        cost_per_token = 0.000003 if "sonnet" in model else 0.000015
        self.usage_stats["total_cost"] += tokens * cost_per_token
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage stats"""
        return self.usage_stats

class ConversationMemory:
    """Simple conversation memory"""
    
    def __init__(self, session_id: str, limit: int = 50):
        self.session_id = session_id
        self.limit = limit
        self.messages = []
    
    def add_message(self, role: str, content: str):
        """Add message"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        if len(self.messages) > self.limit:
            self.messages = self.messages[-self.limit:]
    
    def get_context(self) -> List[Dict]:
        """Get context"""
        return [{"role": msg["role"], "content": msg["content"]} for msg in self.messages]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary"""
        return {
            "session_id": self.session_id,
            "message_count": len(self.messages),
            "user_messages": sum(1 for msg in self.messages if msg["role"] == "user"),
            "assistant_messages": sum(1 for msg in self.messages if msg["role"] == "assistant")
        }
    
    def save_to_file(self) -> str:
        """Save to file"""
        filepath = f"thor/memory/{self.session_id}.json"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump({
                "session_id": self.session_id,
                "messages": self.messages
            }, f, indent=2)
        
        return filepath
    
    def load_from_file(self, filepath: str):
        """Load from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.messages = data["messages"]
    
    def clear(self):
        """Clear messages"""
        self.messages.clear()
    
    def export_markdown(self) -> str:
        """Export to markdown"""
        filepath = f"thor/memory/{self.session_id}.md"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            f.write(f"# Conversation: {self.session_id}\n\n")
            for msg in self.messages:
                role = "User" if msg["role"] == "user" else "Assistant"
                f.write(f"## {role}\n\n{msg['content']}\n\n---\n\n")
        
        return filepath

class ArtifactManager:
    """Simple artifact manager"""
    
    def __init__(self):
        self.artifacts = {}
    
    def create_artifact(self, name: str, content: str, artifact_type: str) -> str:
        """Create artifact"""
        import uuid
        artifact_id = str(uuid.uuid4())
        
        self.artifacts[artifact_id] = {
            "id": artifact_id,
            "name": name,
            "content": content,
            "type": artifact_type,
            "created_at": datetime.now().isoformat()
        }
        
        return artifact_id
    
    def get_artifact(self, artifact_id: str) -> Optional[Dict]:
        """Get artifact"""
        return self.artifacts.get(artifact_id)
    
    def list_artifacts(self) -> List[Dict]:
        """List artifacts"""
        return list(self.artifacts.values())

class SwarmManager:
    """Simple swarm manager"""
    
    def __init__(self):
        self.agents = {}
    
    async def deploy_agent(self, agent_type: str, config: Dict = None) -> str:
        """Deploy agent"""
        import uuid
        agent_id = str(uuid.uuid4())
        
        self.agents[agent_id] = {
            "id": agent_id,
            "type": agent_type,
            "status": "deployed",
            "config": config or {}
        }
        
        return agent_id
    
    async def get_status(self) -> Dict[str, Any]:
        """Get status"""
        return {
            "agents": {"total": len(self.agents)},
            "tasks": {"total": 0}
        }
    
    async def orchestrate_task(self, task: str, agents: List[str], mode: str) -> Dict[str, Any]:
        """Orchestrate task"""
        return {
            "task": task,
            "agents": agents,
            "mode": mode,
            "status": "completed"
        }
    
    def shutdown(self):
        """Shutdown"""
        pass

class ArgusOrchestrator:
    """Simple Argus orchestrator"""
    
    def __init__(self):
        self.running = False
    
    def shutdown(self):
        """Shutdown"""
        pass