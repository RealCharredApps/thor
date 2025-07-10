#!/usr/bin/env python3
"""
THOR Example Usage Script
Demonstrates how to use THOR programmatically
"""

import asyncio
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.thor_client import ThorClient


async def main():
    """Example THOR usage"""
    
    # Initialize THOR
    thor = ThorClient(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        project_root="."
    )
    
    try:
        # Setup environment
        print("Setting up THOR environment...")
        await thor.setup_environment()
        
        # Example 1: Simple chat
        response = await thor.chat(
            "Analyze the current project structure and suggest improvements",
            agent="thor_architect"
        )
        print("Analysis Response:", response)
        
        # Example 2: Code generation
        response = await thor.chat(
            "Create a simple FastAPI hello world endpoint in app/main.py",
            agent="code_wizard"
        )
        print("Code Generation Response:", response)
        
        # Example 3: Security analysis
        response = await thor.chat(
            "Perform a security audit of this project",
            agent="security_guardian"
        )
        print("Security Analysis:", response)
        
    finally:
        await thor.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
