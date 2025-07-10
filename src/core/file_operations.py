# src/core/file_operations.py
import os
import subprocess
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path
import fnmatch
import ast

class FileOperations:
    """Enhanced file operations with security and best practices"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.safe_commands = {
            'ls', 'dir', 'pwd', 'whoami', 'date', 'echo', 'cat', 'head', 'tail',
            'find', 'grep', 'wc', 'sort', 'uniq', 'git', 'npm', 'pip', 'python',
            'node', 'java', 'javac', 'gcc', 'make', 'cmake', 'curl', 'wget'
        }
    
    def read_file(self, file_path: str) -> str:
        """Read file with comprehensive error handling"""
        try:
            path = Path(file_path)
            if not path.exists():
                return f"❌ File not found: {file_path}"
            
            if not path.is_file():
                return f"❌ Path is not a file: {file_path}"
            
            # Check file size (max 10MB)
            if path.stat().st_size > 10 * 1024 * 1024:
                return f"❌ File too large (>10MB): {file_path}"
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.logger.info(f"Read file: {file_path}")
            return content
            
        except UnicodeDecodeError:
            try:
                with open(path, 'r', encoding='latin-1') as f:
                    content = f.read()
                return content
            except Exception as e:
                return f"❌ Error reading file (binary?): {str(e)}"
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return f"❌ Error reading file: {str(e)}"
    
    def write_file(self, file_path: str, content: str) -> str:
        """Write file with backup and safety checks"""
        try:
            path = Path(file_path)
            
            # Create backup if file exists
            if path.exists():
                backup_path = path.with_suffix(path.suffix + '.backup')
                path.replace(backup_path)
                self.logger.info(f"Created backup: {backup_path}")
            
            # Create directory if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Written file: {file_path}")
            return f"✅ File written successfully: {file_path}"
            
        except Exception as e:
            self.logger.error(f"Error writing file {file_path}: {e}")
            return f"❌ Error writing file: {str(e)}"
    
    def list_files(self, directory: str = ".") -> str:
        """List files with enhanced information"""
        try:
            path = Path(directory)
            if not path.exists():
                return f"❌ Directory not found: {directory}"
            
            if not path.is_dir():
                return f"❌ Path is not a directory: {directory}"
            
            files = []
            for item in sorted(path.iterdir()):
                if item.is_file():
                    size = item.stat().st_size
                    files.append(f"📄 {item.name} ({size} bytes)")
                elif item.is_dir():
                    files.append(f"📁 {item.name}/")
            
            if not files:
                return f"📂 Empty directory: {directory}"
            
            return f"📂 Contents of {directory}:\n" + "\n".join(files)
            
        except Exception as e:
            self.logger.error(f"Error listing files in {directory}: {e}")
            return f"❌ Error listing files: {str(e)}"
    
    def create_directory(self, directory_path: str) -> str:
        """Create directory with proper error handling"""
        try:
            path = Path(directory_path)
            path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created directory: {directory_path}")
            return f"✅ Directory created: {directory_path}"
            
        except Exception as e:
            self.logger.error(f"Error creating directory {directory_path}: {e}")
            return f"❌ Error creating directory: {str(e)}"
    
    def run_command(self, command: str) -> str:
        """Run command with security restrictions"""
        try:
            # Security check
            cmd_parts = command.split()
            if not cmd_parts:
                return "❌ Empty command"
            
            base_command = cmd_parts[0]
            if base_command not in self.safe_commands:
                return f"❌ Command not allowed for security: {base_command}"
            
            # Run command with timeout
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.getcwd()
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n❌ Error: {result.stderr}"
            
            self.logger.info(f"Executed command: {command}")
            return output or "✅ Command executed successfully (no output)"
            
        except subprocess.TimeoutExpired:
            return "❌ Command timeout (30 seconds)"
        except Exception as e:
            self.logger.error(f"Error running command {command}: {e}")
            return f"❌ Error running command: {str(e)}"
    
    def search_files(self, pattern: str, directory: str = ".") -> str:
        """Search files for pattern with advanced options"""
        try:
            path = Path(directory)
            if not path.exists():
                return f"❌ Directory not found: {directory}"
            
            matches = []
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    try:
                        # Skip binary files
                        if file_path.suffix in ['.exe', '.bin', '.so', '.dll']:
                            continue
                        
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if pattern.lower() in content.lower():
                                matches.append(str(file_path))
                    except (UnicodeDecodeError, PermissionError):
                        continue
            
            if not matches:
                return f"❌ No matches found for pattern: {pattern}"
            
            return f"🔍 Found {len(matches)} matches for '{pattern}':\n" + "\n".join(matches)
            
        except Exception as e:
            self.logger.error(f"Error searching files: {e}")
            return f"❌ Error searching files: {str(e)}"
    
    def analyze_code(self, file_path: str) -> str:
        """Analyze code file for best practices and issues"""
        try:
            content = self.read_file(file_path)
            if content.startswith("❌"):
                return content
            
            path = Path(file_path)
            analysis = {
                "file": file_path,
                "size": len(content),
                "lines": len(content.splitlines()),
                "extension": path.suffix,
                "issues": [],
                "suggestions": []
            }
            
            # Language-specific analysis
            if path.suffix == '.py':
                analysis.update(self._analyze_python_code(content))
            elif path.suffix in ['.js', '.ts']:
                analysis.update(self._analyze_javascript_code(content))
            elif path.suffix in ['.java']:
                analysis.update(self._analyze_java_code(content))
            
            return json.dumps(analysis, indent=2)
            
        except Exception as e:
            self.logger.error(f"Error analyzing code {file_path}: {e}")
            return f"❌ Error analyzing code: {str(e)}"
    
    def _analyze_python_code(self, content: str) -> Dict:
        """Analyze Python code specifically"""
        issues = []
        suggestions = []
        
        try:
            # Parse AST
            tree = ast.parse(content)
            
            # Check for common issues
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not ast.get_docstring(node):
                        issues.append(f"Function '{node.name}' missing docstring")
                
                if isinstance(node, ast.ClassDef):
                    if not ast.get_docstring(node):
                        issues.append(f"Class '{node.name}' missing docstring")
            
            # Check for imports
            if 'import *' in content:
                issues.append("Avoid wildcard imports")
            
            # Check for TODO/FIXME
            for i, line in enumerate(content.splitlines(), 1):
                if 'TODO' in line.upper() or 'FIXME' in line.upper():
                    issues.append(f"Line {i}: {line.strip()}")
            
        except SyntaxError as e:
            issues.append(f"Syntax error: {str(e)}")
        
        return {"issues": issues, "suggestions": suggestions}
    
    def _analyze_javascript_code(self, content: str) -> Dict:
        """Analyze JavaScript code specifically"""
        issues = []
        suggestions = []
        
        # Basic checks
        if 'var ' in content:
            issues.append("Consider using 'let' or 'const' instead of 'var'")
        
        if '== ' in content:
            issues.append("Consider using '===' for strict equality")
        
        if 'console.log' in content:
            suggestions.append("Remove console.log statements in production")
        
        return {"issues": issues, "suggestions": suggestions}
    
    def _analyze_java_code(self, content: str) -> Dict:
        """Analyze Java code specifically"""
        issues = []
        suggestions = []
        
        # Basic checks
        if 'System.out.println' in content:
            suggestions.append("Consider using a logging framework instead of System.out.println")
        
        if 'catch (Exception e)' in content:
            suggestions.append("Consider catching specific exceptions instead of generic Exception")
        
        return {"issues": issues, "suggestions": suggestions}