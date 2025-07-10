            
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "command": " ".join(command),
                "returncode": process.returncode,
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
                "success": process.returncode == 0
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _tool_git_push(self) -> Dict[str, Any]:
        """Git push to remote"""
        return await self.client._tool_run_command("git push")
    
    async def _tool_git_pull(self) -> Dict[str, Any]:
        """Git pull from remote"""
        return await self.client._tool_run_command("git pull")
    
    async def _tool_git_branch(self, branch_name: str = None, action: str = "list") -> Dict[str, Any]:
        """Git branch operations"""
        if action == "list":
            return await self.client._tool_run_command("git branch -a")
        elif action == "create" and branch_name:
            return await self.client._tool_run_command(f"git checkout -b {branch_name}")
        elif action == "switch" and branch_name:
            return await self.client._tool_run_command(f"git checkout {branch_name}")
        elif action == "delete" and branch_name:
            return await self.client._tool_run_command(f"git branch -d {branch_name}")
        else:
            return {"error": "Invalid branch action or missing branch name", "success": False}
    
    async def _tool_analyze_code(self, file_path: str) -> str:
        """Analyze code using Claude"""
        try:
            content = await self.client._tool_read_file(file_path)
            if content.startswith("Error"):
                return content
            
            analysis_prompt = f"""
            Analyze this code file for quality, security, performance, and maintainability:
            
            File: {file_path}
            
            ```
            {content}
            ```
            
            Provide comprehensive analysis including:
            1. **Code Quality**: Structure, readability, naming conventions
            2. **Security Issues**: Vulnerabilities, input validation, authentication
            3. **Performance**: Bottlenecks, optimization opportunities
            4. **Maintainability**: Documentation, complexity, modularity
            5. **Best Practices**: Adherence to language/framework conventions
            6. **Bugs/Issues**: Potential runtime errors, logic issues
            7. **Recommendations**: Specific improvement suggestions
            
            Be thorough and provide actionable insights.
            """
            
            analysis = await self.client.chat(
                analysis_prompt,
                agent="code_wizard",
                use_tools=False,
                include_context=False
            )
            
            return f"Code Analysis for {file_path}:\n\n{analysis}"
            
        except Exception as e:
            return f"Error analyzing code: {str(e)}"
    
    async def _tool_generate_tests(self, file_path: str, test_framework: str = "auto") -> str:
        """Generate comprehensive tests for code file"""
        try:
            content = await self.client._tool_read_file(file_path)
            if content.startswith("Error"):
                return content
            
            # Determine test framework based on file type and project
            if test_framework == "auto":
                if file_path.endswith('.py'):
                    test_framework = "pytest"
                elif file_path.endswith(('.js', '.ts')):
                    test_framework = "jest"
                elif file_path.endswith('.go'):
                    test_framework = "go test"
                else:
                    test_framework = "generic"
            
            test_prompt = f"""
            Generate comprehensive unit tests for this code file:
            
            File: {file_path}
            Test Framework: {test_framework}
            
            ```
            {content}
            ```
            
            Generate tests that include:
            1. **Unit Tests**: Test all functions/methods individually
            2. **Edge Cases**: Boundary conditions, empty inputs, invalid data
            3. **Error Handling**: Exception scenarios, error conditions
            4. **Integration Tests**: Function interactions where applicable
            5. **Performance Tests**: If relevant for the code
            6. **Security Tests**: Input validation, injection attacks if applicable
            7. **Mock/Stub Usage**: For external dependencies
            
            Provide:
            - Complete test file with proper naming convention
            - Test setup and teardown if needed
            - Clear test descriptions and assertions
            - Code coverage for all paths
            
            Return only the complete test file code.
            """
            
            tests = await self.client.chat(
                test_prompt,
                agent="code_wizard",
                use_tools=False,
                include_context=False
            )
            
            # Save test file
            test_file_path = self._get_test_file_path(file_path, test_framework)
            await self.client._tool_write_file(test_file_path, tests)
            
            return f"Generated tests saved to: {test_file_path}\n\n{tests}"
            
        except Exception as e:
            return f"Error generating tests: {str(e)}"
    
    async def _tool_refactor_code(self, file_path: str, refactor_type: str = "improve") -> str:
        """Refactor code for better quality"""
        try:
            content = await self.client._tool_read_file(file_path)
            if content.startswith("Error"):
                return content
            
            refactor_prompt = f"""
            Refactor this code to {refactor_type}:
            
            File: {file_path}
            Refactoring Goal: {refactor_type}
            
            ```
            {content}
            ```
            
            Apply these refactoring principles:
            1. **Clean Code**: Improve readability and maintainability
            2. **SOLID Principles**: Single responsibility, open/closed, etc.
            3. **DRY**: Remove code duplication
            4. **Performance**: Optimize for speed and memory
            5. **Security**: Fix security vulnerabilities
            6. **Best Practices**: Follow language/framework conventions
            7. **Error Handling**: Robust error management
            8. **Documentation**: Add clear comments and docstrings
            
            Specific improvements:
            - Extract methods/functions for better modularity
            - Improve variable and function naming
            - Add type hints (if applicable)
            - Optimize algorithms and data structures
            - Add proper error handling
            - Remove dead code
            - Improve code organization
            
            Return the complete refactored code.
            """
            
            refactored = await self.client.chat(
                refactor_prompt,
                agent="code_wizard",
                use_tools=False,
                include_context=False
            )
            
            # Create backup
            backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            await self.client._tool_copy_file(file_path, backup_path)
            
            # Save refactored code
            await self.client._tool_write_file(file_path, refactored)
            
            return f"Code refactored successfully!\nBackup saved to: {backup_path}\n\nRefactored code:\n{refactored}"
            
        except Exception as e:
            return f"Error refactoring code: {str(e)}"
    
    async def _tool_format_code(self, file_path: str) -> str:
        """Format code using appropriate formatter"""
        try:
            if file_path.endswith('.py'):
                result = await self.client._tool_run_command(f"black {file_path}")
                if not result.get("success"):
                    # Try autopep8 as fallback
                    result = await self.client._tool_run_command(f"autopep8 --in-place {file_path}")
            elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                result = await self.client._tool_run_command(f"npx prettier --write {file_path}")
            elif file_path.endswith('.go'):
                result = await self.client._tool_run_command(f"gofmt -w {file_path}")
            elif file_path.endswith(('.cpp', '.c', '.h')):
                result = await self.client._tool_run_command(f"clang-format -i {file_path}")
            else:
                return f"No formatter available for {file_path}"
            
            if result.get("success"):
                return f"Successfully formatted {file_path}"
            else:
                return f"Error formatting {file_path}: {result.get('stderr', 'Unknown error')}"
                
        except Exception as e:
            return f"Error formatting code: {str(e)}"
    
    async def _tool_lint_code(self, file_path: str) -> str:
        """Lint code for issues"""
        try:
            results = []
            
            if file_path.endswith('.py'):
                # Try multiple Python linters
                linters = [
                    ("flake8", f"flake8 {file_path}"),
                    ("pylint", f"pylint {file_path}"),
                    ("mypy", f"mypy {file_path}")
                ]
                
                for linter_name, command in linters:
                    result = await self.client._tool_run_command(command)
                    if result.get("stdout") or result.get("stderr"):
                        results.append(f"{linter_name} results:\n{result.get('stdout', '')}{result.get('stderr', '')}")
            
            elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                result = await self.client._tool_run_command(f"npx eslint {file_path}")
                if result.get("stdout") or result.get("stderr"):
                    results.append(f"ESLint results:\n{result.get('stdout', '')}{result.get('stderr', '')}")
            
            elif file_path.endswith('.go'):
                # Go vet and golint
                vet_result = await self.client._tool_run_command(f"go vet {file_path}")
                lint_result = await self.client._tool_run_command(f"golint {file_path}")
                
                if vet_result.get("stderr"):
                    results.append(f"go vet results:\n{vet_result.get('stderr')}")
                if lint_result.get("stdout"):
                    results.append(f"golint results:\n{lint_result.get('stdout')}")
            
            if results:
                return f"Linting results for {file_path}:\n\n" + "\n\n".join(results)
            else:
                return f"No linting issues found in {file_path}"
                
        except Exception as e:
            return f"Error linting code: {str(e)}"
    
    async def _tool_create_project_structure(self, project_type: str, project_name: str = None) -> str:
        """Create project structure for different types"""
        try:
            if not project_name:
                project_name = self.project_root.name
            
            structures = {
                "python": {
                    "dirs": ["src", "tests", "docs", "scripts", "data", "config"],
                    "files": {
                        "requirements.txt": "",
                        "setup.py": self._get_python_setup_template(project_name),
                        "pyproject.toml": self._get_pyproject_template(project_name),
                        "README.md": f"# {project_name}\n\nProject description here.",
                        ".gitignore": self._get_python_gitignore(),
                        "src/__init__.py": "",
                        "tests/__init__.py": "",
                        "tests/test_main.py": self._get_python_test_template()
                    }
                },
                "node": {
                    "dirs": ["src", "test", "dist", "docs"],
                    "files": {
                        "package.json": self._get_package_json_template(project_name),
                        "tsconfig.json": self._get_tsconfig_template(),
                        "README.md": f"# {project_name}\n\nProject description here.",
                        ".gitignore": self._get_node_gitignore(),
                        "src/index.ts": "export default {};\n",
                        "test/index.test.ts": self._get_jest_test_template()
                    }
                },
                "fastapi": {
                    "dirs": ["app", "tests", "docs", "scripts", "alembic/versions"],
                    "files": {
                        "requirements.txt": self._get_fastapi_requirements(),
                        "app/main.py": self._get_fastapi_main_template(),
                        "app/__init__.py": "",
                        "app/api/__init__.py": "",
                        "app/api/v1/__init__.py": "",
                        "app/api/v1/endpoints/__init__.py": "",
                        "app/core/__init__.py": "",
                        "app/core/config.py": self._get_fastapi_config_template(),
                        "app/models/__init__.py": "",
                        "app/schemas/__init__.py": "",
                        "tests/__init__.py": "",
                        "README.md": f"# {project_name} API\n\nFastAPI application.",
                        ".gitignore": self._get_python_gitignore(),
                        "docker-compose.yml": self._get_docker_compose_template(),
                        "Dockerfile": self._get_dockerfile_template()
                    }
                },
                "react": {
                    "dirs": ["src", "public", "src/components", "src/pages", "src/hooks", "src/utils"],
                    "files": {
                        "package.json": self._get_react_package_template(project_name),
                        "tsconfig.json": self._get_react_tsconfig_template(),
                        "src/App.tsx": self._get_react_app_template(),
                        "src/index.tsx": self._get_react_index_template(),
                        "public/index.html": self._get_react_html_template(project_name),
                        "README.md": f"# {project_name}\n\nReact application.",
                        ".gitignore": self._get_node_gitignore()
                    }
                }
            }
            
            if project_type not in structures:
                return f"Unknown project type: {project_type}. Available: {', '.join(structures.keys())}"
            
            structure = structures[project_type]
            
            # Create directories
            for dir_path in structure["dirs"]:
                await self.client._tool_create_directory(dir_path)
            
            # Create files
            for file_path, content in structure["files"].items():
                await self.client._tool_write_file(file_path, content)
            
            return f"Successfully created {project_type} project structure for {project_name}"
            
        except Exception as e:
            return f"Error creating project structure: {str(e)}"
    
    async def _tool_install_dependencies(self, package_manager: str = "auto") -> Dict[str, Any]:
        """Install project dependencies"""
        try:
            if package_manager == "auto":
                # Detect package manager
                if (self.project_root / "package.json").exists():
                    package_manager = "npm"
                elif (self.project_root / "requirements.txt").exists():
                    package_manager = "pip"
                elif (self.project_root / "pyproject.toml").exists():
                    package_manager = "pip"
                elif (self.project_root / "go.mod").exists():
                    package_manager = "go"
                elif (self.project_root / "Cargo.toml").exists():
                    package_manager = "cargo"
                else:
                    return {"error": "Could not detect package manager", "success": False}
            
            commands = {
                "npm": "npm install",
                "yarn": "yarn install",
                "pip": "pip install -r requirements.txt",
                "pipenv": "pipenv install",
                "poetry": "poetry install",
                "go": "go mod download",
                "cargo": "cargo build"
            }
            
            if package_manager not in commands:
                return {"error": f"Unknown package manager: {package_manager}", "success": False}
            
            return await self.client._tool_run_command(commands[package_manager])
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _tool_build_project(self, build_type: str = "auto") -> Dict[str, Any]:
        """Build the project"""
        try:
            if build_type == "auto":
                # Detect build system
                if (self.project_root / "package.json").exists():
                    build_type = "npm"
                elif (self.project_root / "setup.py").exists():
                    build_type = "python"
                elif (self.project_root / "go.mod").exists():
                    build_type = "go"
                elif (self.project_root / "Cargo.toml").exists():
                    build_type = "cargo"
                elif (self.project_root / "Makefile").exists():
                    build_type = "make"
                else:
                    return {"error": "Could not detect build system", "success": False}
            
            commands = {
                "npm": "npm run build",
                "yarn": "yarn build",
                "python": "python setup.py build",
                "go": "go build",
                "cargo": "cargo build --release",
                "make": "make"
            }
            
            if build_type not in commands:
                return {"error": f"Unknown build type: {build_type}", "success": False}
            
            return await self.client._tool_run_command(commands[build_type])
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _tool_deploy_project(self, target: str = "local") -> Dict[str, Any]:
        """Deploy the project"""
        try:
            if target == "local":
                # Local deployment - just run the application
                if (self.project_root / "package.json").exists():
                    return await self.client._tool_run_command("npm start")
                elif (self.project_root / "app/main.py").exists():
                    return await self.client._tool_run_command("uvicorn app.main:app --reload")
                elif (self.project_root / "main.py").exists():
                    return await self.client._tool_run_command("python main.py")
                else:
                    return {"error": "Could not determine how to run the application", "success": False}
            
            elif target == "docker":
                # Docker deployment
                build_result = await self.client._tool_run_command("docker build -t thor-app .")
                if not build_result.get("success"):
                    return build_result
                
                return await self.client._tool_run_command("docker run -p 8000:8000 thor-app")
            
            else:
                return {"error": f"Unknown deployment target: {target}", "success": False}
                
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _tool_query_database(self, query: str, database_url: str = None) -> Union[List[Dict], str]:
        """Execute database query"""
        try:
            # This would need actual database connection logic
            return "Database querying not implemented yet - requires database connection setup"
        except Exception as e:
            return f"Error querying database: {str(e)}"
    
    async def _tool_backup_database(self, backup_path: str = None) -> str:
        """Backup database"""
        try:
            if not backup_path:
                backup_path = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            
            # This would need actual database backup logic
            return f"Database backup not implemented yet - would save to {backup_path}"
        except Exception as e:
            return f"Error backing up database: {str(e)}"
    
    async def _tool_parallel_process(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple tasks in parallel"""
        try:
            async def process_task(task):
                task_type = task.get("type")
                task_args = task.get("args", {})
                
                if task_type in self.client.tools_registry:
                    result = await self.client.tools_registry[task_type](**task_args)
                    return {"task": task, "result": result, "success": True}
                else:
                    return {"task": task, "error": f"Unknown task type: {task_type}", "success": False}
            
            results = await asyncio.gather(*[process_task(task) for task in tasks], return_exceptions=True)
            
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    processed_results.append({"error": str(result), "success": False})
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            return [{"error": str(e), "success": False}]
    
    async def _tool_monitor_system(self) -> Dict[str, Any]:
        """Monitor system resources"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                },
                "processes": len(psutil.pids()),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _tool_optimize_performance(self, target: str = "code") -> str:
        """Optimize performance of code or system"""
        try:
            if target == "code":
                # Analyze all Python files for performance issues
                python_files = await self.client._tool_list_files(".", "**/*.py")
                if isinstance(python_files, str):
                    return python_files
                
                optimization_results = []
                
                for file_path in python_files[:5]:  # Limit to avoid overwhelming
                    analysis = await self._tool_analyze_code(file_path)
                    if "performance" in analysis.lower():
                        optimization_results.append(f"Performance issues found in {file_path}")
                
                return f"Performance optimization analysis complete. Found issues in {len(optimization_results)} files."
            
            elif target == "system":
                system_info = await self._tool_monitor_system()
                suggestions = []
                
                if system_info.get("memory", {}).get("percent", 0) > 80:
                    suggestions.append("High memory usage detected - consider closing unused applications")
                
                if system_info.get("disk", {}).get("percent", 0) > 90:
                    suggestions.append("Low disk space - consider cleaning up files")
                
                if system_info.get("cpu_percent", 0) > 80:
                    suggestions.append("High CPU usage - check for resource-intensive processes")
                
                return "System optimization suggestions:\n" + "\n".join(suggestions) if suggestions else "System performance looks good"
            
            else:
                return f"Unknown optimization target: {target}"
                
        except Exception as e:
            return f"Error optimizing performance: {str(e)}"
    
    def _get_test_file_path(self, file_path: str, framework: str) -> str:
        """Generate appropriate test file path"""
        file_stem = Path(file_path).stem
        
        if framework == "pytest":
            return f"tests/test_{file_stem}.py"
        elif framework == "jest":
            return f"tests/{file_stem}.test.js"
        elif framework == "go test":
            return f"{file_stem}_test.go"
        else:
            return f"tests/test_{file_stem}.txt"
    
    # Template methods for project structure
    def _get_python_setup_template(self, name: str) -> str:
        return f'''"""Setup script for {name}"""
from setuptools import setup, find_packages

setup(
    name="{name}",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.8",
    author="THOR",
    description="A Python project generated by THOR",
)
'''
    
    def _get_pyproject_template(self, name: str) -> str:
        return f'''[tool.poetry]
name = "{name}"
version = "0.1.0"
description = "A Python project generated by THOR"
authors = ["THOR <thor@example.com>"]

[tool.poetry.dependencies]
python = "^3.8"

[tool.poetry.dev-dependencies]
pytest = "^7.0"
black = "^22.0"
flake8 = "^4.0"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
'''
    
    def _get_python_gitignore(self) -> str:
        return '''# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
'''
    
    def _get_python_test_template(self) -> str:
        return '''"""Test module"""
import pytest


def test_example():
    """Example test"""
    assert True


class TestExample:
    """Example test class"""
    
    def test_method(self):
        """Example test method"""
        assert 1 + 1 == 2
'''
    
    def _get_fastapi_requirements(self) -> str:
        return '''fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
alembic==1.13.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pytest==7.4.3
httpx==0.25.2
'''
    
    def _get_fastapi_main_template(self) -> str:
        return '''"""FastAPI application main module"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="THOR Generated API",
    description="API generated by THOR",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hello from THOR!"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    def _get_fastapi_config_template(self) -> str:
        return '''"""Application configuration"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    app_name: str = "THOR API"
    debug: bool = False
    secret_key: str = "your-secret-key-here"
    database_url: str = "sqlite:///./thor.db"
    
    class Config:
        env_file = ".env"


settings = Settings()
'''
    
    def _get_docker_compose_template(self) -> str:
        return '''version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/thor
    depends_on:
      - db
    volumes:
      - .:/app
    
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=thor
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
'''
    
    def _get_dockerfile_template(self) -> str:
        return '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
