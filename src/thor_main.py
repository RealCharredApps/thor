# src/thor_main.py
#!/usr/bin/env python3
import asyncio
import click
import sys
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.thor_client import ThorClient

console = Console()

class ThorCLI:
    def __init__(self):
        self.client = None
        self.console = console
        
    async def initialize(self, config_path: str = None):
        """Initialize THOR client"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Initializing THOR...", total=None)
            
            try:
                self.client = ThorClient(config_path)
                progress.update(task, description="THOR initialized successfully!")
                return True
            except Exception as e:
                self.console.print(f"[red]Error initializing THOR: {e}[/red]")
                return False
    
    async def interactive_mode(self):
        """Run interactive chat mode"""
        self.console.print(Panel.fit(
            "[bold blue]THOR AI Development Assistant[/bold blue]\n"
            "Type 'help' for commands, 'exit' to quit",
            border_style="blue"
        ))
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold green]You[/bold green]")
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    self.console.print("[yellow]Goodbye![/yellow]")
                    break
                
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                if user_input.lower() == 'clear':
                    self.console.clear()
                    continue
                
                # Process with THOR
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task("Thinking...", total=None)
                    
                    response = await self.client.chat(user_input)
                    
                    progress.update(task, description="Done!")
                
                # Display response
                self.console.print("\n[bold blue]THOR:[/bold blue]")
                self.console.print(Markdown(response))
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use 'exit' to quit[/yellow]")
            except Exception as e:
                self.console.print(f"\n[red]Error: {e}[/red]")
    
    def show_help(self):
        """Show help information"""
        help_text = """
# THOR Commands

- **help** - Show this help message
- **clear** - Clear the screen
- **exit/quit/q** - Exit THOR

# Example queries:
- "Create a Python FastAPI application"
- "Analyze the code in main.py"
- "Search for TODO comments in all Python files"
- "Run pytest in the current directory"
- "Create a new React component"
        """
        self.console.print(Markdown(help_text))

@click.command()
@click.option('--config', '-c', help='Path to configuration file')
@click.option('--no-interactive', '-n', is_flag=True, help='Non-interactive mode')
@click.argument('query', required=False)
def main(config, no_interactive, query):
    """THOR - AI Development Assistant"""
    cli = ThorCLI()
    
    # Run async main
    async def async_main():
        # Initialize
        if not await cli.initialize(config):
            sys.exit(1)
        
        if query or no_interactive:
            # Single query mode
            if query:
                response = await cli.client.chat(query)
                console.print(Markdown(response))
        else:
            # Interactive mode
            await cli.interactive_mode()
    
    # Run
    asyncio.run(async_main())

if __name__ == '__main__':
    main()