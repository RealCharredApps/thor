        """Load and cache project context"""
        context_data = {
            "files": [],
            "structure": {},
            "dependencies": {},
            "git_info": {},
            "last_updated": datetime.now().isoformat()
        }
        
        try:
            # Scan project files
            important_extensions = {
                '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss',
                '.json', '.yml', '.yaml', '.md', '.txt', '.sql', '.sh', '.bat',
                '.dockerfile', '.go', '.rs', '.java', '.cpp', '.c', '.h'
            }
            
            for file_path in self.project_root.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in important_extensions:
                    relative_path = file_path.relative_to(self.project_root)
                    
                    # Skip common ignore patterns
                    if any(part.startswith('.') for part in relative_path.parts):
                        continue
                    if any(part in ['node_modules', '__pycache__', '.git', 'venv', 'env'] for part in relative_path.parts):
                        continue
                    
                    file_info = {
                        "path": str(relative_path),
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                        "type": file_path.suffix[1:] if file_path.suffix else "unknown"
                    }
                    context_data["files"].append(file_info)
            
            # Get git information
            try:
                git_status = await self._tool_git_status()
                if git_status.get("success"):
                    context_data["git_info"] = {
                        "status": git_status.get("stdout", ""),
                        "branch": await self._get_git_branch(),
                        "remote": await self._get_git_remote()
                    }
            except:
                pass
            
            # Cache in database
            conn = sqlite3.connect(str(Path(self.project_root) / self.database_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO project_context 
                (id, file_path, content_hash, last_modified, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                "project_overview",
                "project_context.json",
                hashlib.md5(json.dumps(context_data).encode()).hexdigest(),
                datetime.now(),
                json.dumps(context_data)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.warning(f"Could not load full project context: {e}")
    
    async def _health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "warnings": [],
            "errors": []
        }
        
        # Check MCP servers
        for server_name, process in self.mcp_servers.items():
            if process.returncode is None:
                health["components"][f"mcp_{server_name}"] = "running"
            else:
                health["components"][f"mcp_{server_name}"] = "stopped"
                health["errors"].append(f"MCP server {server_name} is not running")
        
        # Check Anthropic API
        try:
            test_message = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            health["components"]["anthropic_api"] = "connected"
        except Exception as e:
            health["components"]["anthropic_api"] = "error"
            health["errors"].append(f"Anthropic API error: {str(e)}")
        
        # Check filesystem access
        try:
            test_file = self.project_root / "thor_health_check.tmp"
            test_file.write_text("test")
            test_file.unlink()
            health["components"]["filesystem"] = "accessible"
        except Exception as e:
            health["components"]["filesystem"] = "error"
            health["errors"].append(f"Filesystem error: {str(e)}")
        
        # Check database
        try:
            conn = sqlite3.connect(str(Path(self.project_root) / self.database_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversations")
            conn.close()
            health["components"]["database"] = "accessible"
        except Exception as e:
            health["components"]["database"] = "error"
            health["errors"].append(f"Database error: {str(e)}")
        
        # Determine overall status
        if health["errors"]:
            health["status"] = "degraded" if len(health["errors"]) < 2 else "unhealthy"
        
        return health
    
    async def chat(self, 
                   message: str,
                   agent: str = "thor_architect",
                   model: str = None,
                   temperature: float = None,
                   max_tokens: int = None,
                   include_context: bool = True,
                   use_tools: bool = True,
                   autonomous: bool = False) -> str:
        """
        Advanced chat with unlimited capabilities
        """
        
        # Get agent configuration
        if agent not in self.expert_agents:
            agent = "thor_architect"
        
        expert = self.expert_agents[agent]
        
        # Use agent defaults or override
        model = model or self.config.get("anthropic", {}).get("model", "claude-3-5-sonnet-20241022")
        temperature = temperature if temperature is not None else expert.temperature
        max_tokens = max_tokens or expert.max_tokens
        
        try:
            self.console.print(f"[bold cyan]🤖 {expert.name.replace('_', ' ').title()} is thinking...[/bold cyan]")
            
            # Build system prompt
            system_prompt = expert.system_prompt
            
            # Add project context if requested
            if include_context:
                project_context = await self._get_project_context()
                system_prompt += f"\n\nCurrent Project Context:\n{project_context}"
            
            # Add tool descriptions
            if use_tools:
                tools_description = self._get_tools_description()
                system_prompt += f"\n\nAvailable Tools:\n{tools_description}"
            
            # Prepare tools for Claude API
            tools = self._prepare_anthropic_tools() if use_tools else None
            
            # Create conversation message
            user_msg = ConversationMessage(
                id=str(uuid.uuid4()),
                role="user",
                content=message,
                timestamp=datetime.now(),
                agent=agent,
                metadata={"model": model, "temperature": temperature}
            )
            
            # Call Claude API
            messages = [{"role": "user", "content": message}]
            
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=messages,
                tools=tools
            )
            
            # Handle tool calls iteratively until completion
            final_response = ""
            tool_call_count = 0
            max_tool_calls = 20  # Prevent infinite loops
            
            while True:
                if response.content and response.content[-1].type == "tool_use":
                    if tool_call_count >= max_tool_calls:
                        final_response += "\n\n[Note: Maximum tool call limit reached]"
                        break
                    
                    tool_results = []
                    
                    # Execute all tool calls in this response
                    for content_block in response.content:
                        if content_block.type == "text":
                            final_response += content_block.text
                        elif content_block.type == "tool_use":
                            tool_name = content_block.name
                            tool_args = content_block.input
                            
                            self.console.print(f"[yellow]🔧 Executing: {tool_name}[/yellow]")
                            
                            try:
                                if tool_name in self.tools_registry:
                                    result = await self.tools_registry[tool_name](**tool_args)
                                else:
                                    result = f"Unknown tool: {tool_name}"
                                
                                tool_results.append({
                                    "tool_use_id": content_block.id,
                                    "content": str(result)
                                })
                                
                                self.logger.info(f"Tool executed: {tool_name}")
                                
                            except Exception as e:
                                self.logger.error(f"Tool execution error ({tool_name}): {e}")
                                tool_results.append({
                                    "tool_use_id": content_block.id,
                                    "content": f"Error executing {tool_name}: {str(e)}",
                                    "is_error": True
                                })
                    
                    # Continue conversation with tool results
                    messages.extend([
                        {"role": "assistant", "content": response.content},
                        {"role": "user", "content": tool_results}
                    ])
                    
                    # Get next response
                    response = await asyncio.to_thread(
                        self.anthropic_client.messages.create,
                        model=model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        system=system_prompt,
                        messages=messages,
                        tools=tools
                    )
                    
                    tool_call_count += 1
                    
                else:
                    # No more tool calls, get final text response
                    if response.content:
                        final_response += response.content[0].text
                    break
            
            # Save conversation
            assistant_msg = ConversationMessage(
                id=str(uuid.uuid4()),
                role="assistant", 
                content=final_response,
                timestamp=datetime.now(),
                agent=agent,
                metadata={"model": model, "temperature": temperature, "tool_calls": tool_call_count}
            )
            
            self.conversation_history.extend([user_msg, assistant_msg])
            self._save_conversation_messages([user_msg, assistant_msg])
            
            # If autonomous mode requested, queue follow-up tasks
            if autonomous:
                await self._extract_and_queue_tasks(final_response, agent)
            
            return final_response
            
        except Exception as e:
            self.logger.error(f"Chat error: {e}")
            return f"Error: {str(e)}"
    
    async def _get_project_context(self, max_files: int = 30) -> str:
        """Get comprehensive project context"""
        context_parts = []
        
        try:
            # Get project structure
            structure = await self._tool_list_files(".", "*")
            important_files = [f for f in structure if self._is_important_file(f)]
            
            context_parts.append(f"Project: {self.project_root.name}")
            context_parts.append(f"Total files: {len(important_files)}")
            context_parts.append("\nKey files:")
            
            for file in important_files[:max_files]:
                context_parts.append(f"  - {file}")
            
            if len(important_files) > max_files:
                context_parts.append(f"  ... and {len(important_files) - max_files} more files")
            
            # Get git status
            try:
                git_status = await self._tool_git_status()
                if git_status.get("success") and git_status.get("stdout"):
                    context_parts.append(f"\nGit status:\n{git_status['stdout']}")
            except:
                pass
            
            # Get package/dependency info
            for config_file in ["package.json", "requirements.txt", "pyproject.toml", "Cargo.toml", "go.mod"]:
                try:
                    content = await self._tool_read_file(config_file)
                    context_parts.append(f"\n{config_file}:")
                    # Truncate if too long
                    if len(content) > 500:
                        context_parts.append(content[:500] + "...")
                    else:
                        context_parts.append(content)
                    break
                except:
                    continue
            
        except Exception as e:
            context_parts.append(f"Error getting project context: {e}")
        
        return "\n".join(context_parts)
    
    def _is_important_file(self, file_path: str) -> bool:
        """Check if file is important for context"""
        important_patterns = [
            r'.*\.(py|js|ts|jsx|tsx|go|rs|java|cpp|c|h)$',
            r'.*\.(json|yml|yaml|toml|ini|cfg)$',
            r'.*(README|LICENSE|CHANGELOG|TODO).*',
            r'.*(Dockerfile|docker-compose|Makefile|CMakeLists).*',
            r'.*\.(md|txt)$'
        ]
        
        import re
        return any(re.match(pattern, file_path, re.IGNORECASE) for pattern in important_patterns)
    
    def _get_tools_description(self) -> str:
        """Get description of available tools"""
        descriptions = []
        
        tool_categories = {
            "File Operations": ["read_file", "write_file", "create_directory", "list_files", "search_files"],
            "Git Operations": ["git_status", "git_diff", "git_add", "git_commit", "git_push"],
            "Code Analysis": ["analyze_code", "generate_tests", "refactor_code", "format_code"],
            "Project Management": ["create_project_structure", "install_dependencies", "build_project"],
            "System Operations": ["run_command", "monitor_system", "optimize_performance"]
        }
        
        for category, tools in tool_categories.items():
            available_tools = [tool for tool in tools if tool in self.tools_registry]
            if available_tools:
                descriptions.append(f"{category}: {', '.join(available_tools)}")
        
        return "\n".join(descriptions)
    
    def _prepare_anthropic_tools(self) -> List[Dict[str, Any]]:
        """Prepare tools for Anthropic API"""
        return [
            {
                "name": "read_file",
                "description": "Read the contents of a file",
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
                "name": "create_directory",
                "description": "Create a new directory",
                "input_schema": {
                    "type": "object", 
                    "properties": {
                        "dir_path": {"type": "string", "description": "Path to the directory to create"}
                    },
                    "required": ["dir_path"]
                }
            },
            {
                "name": "list_files",
                "description": "List files in a directory",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "directory": {"type": "string", "description": "Directory to list", "default": "."},
                        "pattern": {"type": "string", "description": "File pattern to match", "default": "*"}
                    }
                }
            },
            {
                "name": "search_files",
                "description": "Search for text in files",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Text to search for"},
                        "file_pattern": {"type": "string", "description": "File pattern to search in", "default": "*.py"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "run_command",
                "description": "Execute a shell command",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Command to execute"},
                        "cwd": {"type": "string", "description": "Working directory", "default": "."}
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "git_status",
                "description": "Get git repository status",
                "input_schema": {"type": "object", "properties": {}}
            },
            {
                "name": "git_commit",
                "description": "Commit changes to git",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Commit message"},
                        "files": {"type": "array", "items": {"type": "string"}, "description": "Files to commit"}
                    },
                    "required": ["message"]
                }
            },
            {
                "name": "analyze_code",
                "description": "Analyze code for quality and issues",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to code file to analyze"}
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "generate_tests",
                "description": "Generate unit tests for code",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to code file to generate tests for"}
                    },
                    "required": ["file_path"]
                }
            }
        ]
    
    async def _extract_and_queue_tasks(self, response: str, agent: str):
        """Extract and queue follow-up tasks from response"""
        # Simple task extraction based on keywords
        task_keywords = [
            "next step", "then we", "should also", "need to", "follow up",
            "additionally", "after that", "once complete", "finally"
        ]
        
        lines = response.split('\n')
        tasks = []
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in task_keywords):
                if len(line) > 10 and not line.startswith('#'):
                    tasks.append({
                        "description": line,
                        "agent": agent,
                        "priority": 2
                    })
        
        # Queue tasks
        for task in tasks:
            await self.task_queue.put(task)
    
    # Tool implementations
    async def _tool_read_file(self, file_path: str) -> str:
        """Read file contents"""
        try:
            full_path = self.project_root / file_path
            if not full_path.exists():
                return f"Error: File {file_path} not found"
            
            async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            return content
            
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"
    
    async def _tool_write_file(self, file_path: str, content: str) -> str:
        """Write content to file"""
        try:
            full_path = self.project_root / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            return f"Successfully wrote {len(content)} characters to {file_path}"
            
        except Exception as e:
            return f"Error writing file {file_path}: {str(e)}"
    
    async def _tool_create_directory(self, dir_path: str) -> str:
        """Create directory"""
        try:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            return f"Successfully created directory: {dir_path}"
            
        except Exception as e:
            return f"Error creating directory {dir_path}: {str(e)}"
    
    async def _tool_list_files(self, directory: str = ".", pattern: str = "*") -> Union[List[str], str]:
        """List files in directory"""
        try:
            dir_path = self.project_root / directory
            if not dir_path.exists():
                return f"Error: Directory {directory} not found"
            
            import glob
            search_path = dir_path / pattern
            files = glob.glob(str(search_path), recursive=True)
            
            # Return relative paths
            result = []
            for file in files:
                rel_path = Path(file).relative_to(self.project_root)
                if Path(file).is_file():
                    result.append(str(rel_path))
            
            return result
            
        except Exception as e:
            return f"Error listing files in {directory}: {str(e)}"
    
    async def _tool_search_files(self, query: str, file_pattern: str = "*.py") -> Union[List[Dict[str, Any]], str]:
        """Search for text in files"""
        try:
            import re
            results = []
            
            files = await self._tool_list_files(".", f"**/{file_pattern}")
            if isinstance(files, str):  # Error message
                return files
            
            for file_path in files:
                try:
                    content = await self._tool_read_file(file_path)
                    if isinstance(content, str) and not content.startswith("Error"):
                        lines = content.split('\n')
                        
                        for line_num, line in enumerate(lines, 1):
                            if re.search(query, line, re.IGNORECASE):
                                results.append({
                                    "file": file_path,
                                    "line": line_num,
                                    "content": line.strip(),
                                    "match": query
                                })
                except:
                    continue
            
            return results
            
        except Exception as e:
            return f"Error searching files: {str(e)}"
    
    async def _tool_run_command(self, command: str, cwd: str = ".") -> Dict[str, Any]:
        """Execute shell command"""
        try:
            work_dir = self.project_root / cwd
            
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=work_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            result = {
                "command": command,
                "returncode": process.returncode,
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
                "success": process.returncode == 0,
                "cwd": str(work_dir)
            }
            
            return result
            
        except Exception as e:
            return {
                "command": command,
                "error": str(e),
                "success": False
            }
    
    async def _tool_git_status(self) -> Dict[str, Any]:
        """Get git status"""
        return await self._tool_run_command("git status --porcelain")
    
    async def _tool_git_diff(self, file_path: str = None) -> Dict[str, Any]:
        """Get git diff"""
        command = "git diff"
        if file_path:
            command += f" {file_path}"
        return await self._tool_run_command(command)
    
    async def _tool_git_add(self, files: List[str] = None) -> Dict[str, Any]:
        """Git add files"""
        if files:
            command = f"git add {' '.join(files)}"
        else:
            command = "git add ."
        return await self._tool_run_command(command)
    
    async def _tool_git_commit(self, message: str, files: List[str] = None) -> Dict[str, Any]:
        """Git commit"""
        if files:
            add_result = await self._tool_git_add(files)
            if not add_result.get("success"):
                return add_result
        
        return await self._tool_run_command(f'git commit -m "{message}"')
    
    async def _get_git_branch(self) -> str:
        """Get current git branch"""
        try:
            result = await self._tool_run_command("git branch --show-current")
            return result.get("stdout", "").strip()
        except:
            return "unknown"
    
    async def _get_git_remote(self) -> str:
        """Get git remote URL"""
        try:
            result = await self._tool_run_command("git remote get-url origin")
            return result.get("stdout", "").strip()
        except:
            return "none"
    
    def _save_conversation_messages(self, messages: List[ConversationMessage]):
        """Save conversation messages to database"""
        conn = sqlite3.connect(str(Path(self.project_root) / self.database_path))
        cursor = conn.cursor()
        
        for msg in messages:
            cursor.execute('''
                INSERT INTO conversations 
                (id, session_id, role, content, agent, timestamp, tokens_used, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                msg.id,
                self.session_id,
                msg.role,
                msg.content,
                msg.agent,
                msg.timestamp,
                msg.tokens_used,
                json.dumps(msg.metadata or {})
            ))
        
        conn.commit()
        conn.close()
    
    async def shutdown(self):
        """Shutdown THOR client"""
        self.console.print("[bold red]⚡ Shutting down THOR...[/bold red]")
        
        # Stop MCP servers
        for name, process in self.mcp_servers.items():
            self.logger.info(f"Stopping MCP server: {name}")
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=5)
            except asyncio.TimeoutError:
                self.logger.warning(f"Force killing MCP server: {name}")
                process.kill()
        
        self.mcp_servers.clear()
        self.console.print("[green]✅ THOR shutdown complete[/green]")
