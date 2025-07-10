#!/usr/bin/env python3
"""
THOR Main Application
Command-line interface for the THOR development assistant
"""
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.thor_client import ThorClient

app = typer.Typer()
console = Console()


@app.command()
def setup(
    project_path: str = typer.Argument(..., help="Path to project directory"),
    api_key: str = typer.Option(None, "--api-key", help="Anthropic API key"),
    config_file: str = typer.Option("config/config.yml", "--config", help="Configuration file path")
):
    """Setup THOR for a project"""
    console.print(Panel("[bold blue]🔨 THOR Setup[/bold blue]", expand=False))
    
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        if typer.confirm(f"Project directory {project_path} doesn't exist. Create it?"):
            project_path.mkdir(parents=True, exist_ok=True)
        else:
            console.print("[red]Setup cancelled[/red]")
            return
    
    # Get API key if not provided
    if not api_key:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            api_key = typer.prompt("Enter your Anthropic API key", hide_input=True)
            if not api_key:
                console.print("[red]API key required[/red]")
                return
    
    # Create configuration
    config_path = project_path / config_file
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    config = {
        "anthropic": {
            "api_key": api_key,
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4000,
            "temperature": 0.3
        },
        "mcp_servers": {
            "filesystem": {
                "name": "filesystem",
                "command": "npx",
                "args": ["@modelcontextprotocol/server-filesystem", str(project_path)],
                "env": {}
            },
            "git": {
                "name": "git",
                "command": "npx", 
                "args": ["@modelcontextprotocol/server-git", str(project_path)],
                "env": {}
            }
        },
        "tools": {
            "enabled": ["filesystem", "git", "code_analysis", "project_management"]
        },
        "autonomous": {
            "enabled": True,
            "max_parallel_tasks": 3,
            "auto_commit": False,
            "backup_before_changes": True
        }
    }
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    console.print(f"[green]✅ THOR configured for project: {project_path}[/green]")
    console.print(f"[blue]📁 Configuration saved to: {config_path}[/blue]")
    console.print(f"[yellow]💡 Run 'thor chat {project_path}' to start development[/yellow]")


@app.command()
def chat(
    project_path: str = typer.Argument(..., help="Path to project directory"),
    agent: str = typer.Option("thor_architect", "--agent", help="Expert agent to use"),
    autonomous: bool = typer.Option(False, "--auto", help="Enable autonomous mode"),
    config_file: str = typer.Option("config/config.yml", "--config", help="Configuration file path")
):
    """Start interactive chat with THOR"""
    asyncio.run(_chat_session(project_path, agent, autonomous, config_file))


async def _chat_session(project_path: str, agent: str, autonomous: bool, config_file: str):
    """Async chat session"""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        console.print(f"[red]Project directory {project_path} not found[/red]")
        return
    
    config_path = project_path / config_file
    if not config_path.exists():
        console.print(f"[red]Configuration file {config_path} not found. Run 'thor setup' first.[/red]")
        return
    
    # Load configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    api_key = config.get("anthropic", {}).get("api_key")
    if not api_key:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            console.print("[red]Anthropic API key not found in config or environment[/red]")
            return
    
    # Initialize THOR
    console.print(Panel("[bold blue]🔨 Initializing THOR...[/bold blue]", expand=False))
    
    thor = ThorClient(
        anthropic_api_key=api_key,
        project_root=str(project_path),
        config_path=config_file
    )
    
    try:
        # Setup environment
        health = await thor.setup_environment()
        
        if health.get("status") != "healthy":
            console.print("[yellow]⚠️  Some components are not healthy but continuing...[/yellow]")
            for error in health.get("errors", []):
                console.print(f"[red]  - {error}[/red]")
        
        # Show available agents
        agents_table = Table(title="Available Expert Agents")
        agents_table.add_column("Name", style="cyan")
        agents_table.add_column("Description", style="green")
        agents_table.add_column("Specializations", style="yellow")
        
        for agent_name, agent_obj in thor.expert_agents.items():
            specializations = ", ".join(agent_obj.specializations or [])
            agents_table.add_row(agent_name, agent_obj.description, specializations)
        
        console.print(agents_table)
        console.print()
        
        # Interactive chat
        console.print(Panel(f"[bold green]🚀 THOR Ready! Using agent: {agent}[/bold green]", expand=False))
        console.print("[blue]Type 'exit' to quit, 'help' for commands, or start chatting![/blue]")
        console.print()
        
        # Setup prompt session with history
        history_file = project_path / ".thor_history"
        session = PromptSession(
            history=FileHistory(str(history_file)),
            auto_suggest=AutoSuggestFromHistory()
        )
        
        while True:
            try:
                # Get user input
                user_input = await asyncio.to_thread(
                    session.prompt,
                    f"[{agent}]> ",
                    multiline=False
                )
                
                if not user_input.strip():
                    continue
                
                # Handle special commands
                if user_input.lower() == 'exit':
                    break
                elif user_input.lower() == 'help':
                    show_help()
                    continue
                elif user_input.startswith('/agent '):
                    new_agent = user_input[7:].strip()
                    if new_agent in thor.expert_agents:
                        agent = new_agent
                        console.print(f"[green]Switched to agent: {agent}[/green]")
                    else:
                        console.print(f"[red]Unknown agent: {new_agent}[/red]")
                    continue
                elif user_input.startswith('/autonomous'):
                    autonomous = not autonomous
                    console.print(f"[yellow]Autonomous mode: {'ON' if autonomous else 'OFF'}[/yellow]")
                    continue
                elif user_input.startswith('/status'):
                    health = await thor._health_check()
                    show_status(health)
                    continue
                elif user_input.startswith('/project'):
                    context = await thor._get_project_context()
                    console.print(Panel(context, title="Project Context", expand=False))
                    continue
                
                # Chat with THOR
                console.print()
                response = await thor.chat(
                    user_input,
                    agent=agent,
                    autonomous=autonomous,
                    use_tools=True,
                    include_context=True
                )
                
                # Display response with syntax highlighting if it contains code
                if "```" in response:
                    display_code_response(response)
                else:
                    console.print(Panel(response, title=f"🤖 {agent.replace('_', ' ').title()}", expand=False))
                
                console.print()
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit[/yellow]")
                continue
            except EOFError:
                break
    
    finally:
        await thor.shutdown()
        console.print("[green]👋 THOR shutdown complete[/green]")


@app.command()
def build(
    project_path: str = typer.Argument(..., help="Path to project directory"),
    project_type: str = typer.Option("auto", "--type", help="Project type to build"),
    features: str = typer.Option("", "--features", help="Comma-separated list of features"),
    config_file: str = typer.Option("config/config.yml", "--config", help="Configuration file path")
):
    """Build a complete project using THOR"""
    asyncio.run(_build_project(project_path, project_type, features, config_file))


async def _build_project(project_path: str, project_type: str, features: str, config_file: str):
    """Build project asynchronously"""
    project_path = Path(project_path).resolve()
    
    # Initialize THOR
    config_path = project_path / config_file
    if not config_path.exists():
        console.print(f"[red]Configuration not found. Run 'thor setup {project_path}' first.[/red]")
        return
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    api_key = config.get("anthropic", {}).get("api_key") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        console.print("[red]Anthropic API key required[/red]")
        return
    
    thor = ThorClient(
        anthropic_api_key=api_key,
        project_root=str(project_path),
        config_path=config_file
    )
    
    try:
        await thor.setup_environment()
        
        # Build project structure
        if project_type != "auto":
            console.print(f"[blue]🏗️  Building {project_type} project...[/blue]")
            
            build_prompt = f"""
            Build a complete {project_type} project with the following features: {features or 'standard features'}.
            
            Requirements:
            1. Create proper project structure
            2. Implement core functionality
            3. Add comprehensive error handling
            4. Include tests
            5. Add documentation
            6. Set up deployment configuration
            
            Make this a production-ready application with best practices.
            """
            
            response = await thor.chat(
                build_prompt,
                agent="thor_architect",
                autonomous=True,
                use_tools=True
            )
            
            console.print(Panel(response, title="🏗️  Project Build Complete", expand=False))
        else:
            console.print("[yellow]Auto-detection of project type not implemented yet[/yellow]")
    
    finally:
        await thor.shutdown()


@app.command()
def analyze(
    project_path: str = typer.Argument(..., help="Path to project directory"),
    analysis_type: str = typer.Option("full", "--type", help="Analysis type: full, security, performance"),
    config_file: str = typer.Option("config/config.yml", "--config", help="Configuration file path")
):
    """Analyze project with THOR experts"""
    asyncio.run(_analyze_project(project_path, analysis_type, config_file))


async def _analyze_project(project_path: str, analysis_type: str, config_file: str):
    """Analyze project asynchronously"""
    project_path = Path(project_path).resolve()
    
    # Initialize THOR
    config_path = project_path / config_file
    if not config_path.exists():
        console.print(f"[red]Configuration not found. Run 'thor setup {project_path}' first.[/red]")
        return
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    api_key = config.get("anthropic", {}).get("api_key") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        console.print("[red]Anthropic API key required[/red]")
        return
    
    thor = ThorClient(
        anthropic_api_key=api_key,
        project_root=str(project_path),
        config_path=config_file
    )
    
    try:
        await thor.setup_environment()
        
        if analysis_type == "security":
            agent = "security_guardian"
            prompt = "Perform a comprehensive security audit of this project. Identify vulnerabilities, security risks, and provide recommendations."
        elif analysis_type == "performance":
            agent = "thor_architect"
            prompt = "Analyze this project for performance issues and optimization opportunities. Check code efficiency, database queries, and system resource usage."
        else:  # full analysis
            agent = "thor_architect"
            prompt = "Perform a comprehensive analysis of this project including code quality, architecture, security, performance, and maintainability. Provide detailed recommendations."
        
        console.print(f"[blue]🔍 Running {analysis_type} analysis...[/blue]")
        
        response = await thor.chat(
            prompt,
            agent=agent,
            use_tools=True,
            include_context=True
        )
        
        console.print(Panel(response, title=f"📊 {analysis_type.title()} Analysis Results", expand=False))
        
        # Save analysis report
        report_file = project_path / f"thor_analysis_{analysis_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(f"# THOR {analysis_type.title()} Analysis Report\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Project: {project_path}\n\n")
            f.write(response)
        
        console.print(f"[green]📄 Analysis report saved to: {report_file}[/green]")
    
    finally:
        await thor.shutdown()


@app.command()
def agents():
    """List available expert agents"""
    agents_info = {
        "thor_architect": {
            "description": "Master architect for complex software development projects",
            "specializations": ["architecture", "full-stack", "scalability", "security"]
        },
        "code_wizard": {
            "description": "Expert programmer for implementation and code quality",
            "specializations": ["programming", "debugging", "optimization", "testing"]
        },
        "devops_master": {
            "description": "DevOps expert for infrastructure and deployment",
            "specializations": ["devops", "infrastructure", "deployment", "monitoring"]
        },
        "security_guardian": {
            "description": "Security expert for application and infrastructure protection",
            "specializations": ["security", "compliance", "encryption", "authentication"]
        },
        "ai_specialist": {
            "description": "AI/ML expert for intelligent application features",
            "specializations": ["ai", "ml", "nlp", "automation"]
        }
    }
    
    table = Table(title="THOR Expert Agents")
    table.add_column("Agent", style="cyan", no_wrap=True)
    table.add_column("Description", style="green")
    table.add_column("Specializations", style="yellow")
    
    for name, info in agents_info.items():
        specializations = ", ".join(info["specializations"])
        table.add_row(name, info["description"], specializations)
    
    console.print(table)


@app.command()
def version():
    """Show THOR version"""
    console.print(Panel("[bold blue]THOR v1.0.0[/bold blue]\nAdvanced MCP Client for Autonomous Software Development", expand=False))


def show_help():
    """Show chat help"""
    help_text = """
[bold blue]THOR Chat Commands:[/bold blue]

[cyan]/agent <name>[/cyan]     - Switch to different expert agent
[cyan]/autonomous[/cyan]       - Toggle autonomous mode
[cyan]/status[/cyan]           - Show system status
[cyan]/project[/cyan]          - Show project context
[cyan]help[/cyan]              - Show this help
[cyan]exit[/cyan]              - Exit chat

[bold yellow]Available Agents:[/bold yellow]
• thor_architect  - Master architect for complex projects
• code_wizard     - Expert programmer for implementation
• devops_master   - DevOps expert for infrastructure
• security_guardian - Security expert for protection
• ai_specialist   - AI/ML expert for intelligent features

[bold green]Tips:[/bold green]
• Ask specific questions for better results
• Use autonomous mode for complex multi-step tasks
• The agents have access to all project files and tools
• THOR can read, write, and execute code autonomously
"""
    console.print(Panel(help_text, expand=False))


def show_status(health: Dict[str, Any]):
    """Show system status"""
    status_color = "green" if health.get("status") == "healthy" else "yellow" if health.get("status") == "degraded" else "red"
    
    status_text = f"[{status_color}]Status: {health.get('status', 'unknown').upper()}[/{status_color}]\n"
    status_text += f"Timestamp: {health.get('timestamp', 'unknown')}\n\n"
    
    status_text += "[bold]Components:[/bold]\n"
    for component, status in health.get("components", {}).items():
        color = "green" if status in ["running", "connected", "accessible"] else "red"
        status_text += f"  {component}: [{color}]{status}[/{color}]\n"
    
    if health.get("errors"):
        status_text += "\n[bold red]Errors:[/bold red]\n"
        for error in health["errors"]:
            status_text += f"  - {error}\n"
    
    console.print(Panel(status_text, title="🔧 THOR Status", expand=False))


def display_code_response(response: str):
    """Display response with code syntax highlighting"""
    parts = response.split("```")
    
    for i, part in enumerate(parts):
        if i % 2 == 0:
            # Regular text
            if part.strip():
                console.print(part.strip())
        else:
            # Code block
            lines = part.split('\n')
            language = lines[0].strip() if lines else ""
            code = '\n'.join(lines[1:]) if len(lines) > 1 else part
            
            if language and code.strip():
                syntax = Syntax(code, language, theme="monokai", line_numbers=True)
                console.print(syntax)
            elif code.strip():
                syntax = Syntax(code, "text", theme="monokai", line_numbers=True)
                console.print(syntax)


def main():
    """Main entry point"""
    app()


if __name__ == "__main__":
    main()
