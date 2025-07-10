# thor/src/swarm_cli.py (Additional CLI for swarm management)
import asyncio
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.swarm_manager import SwarmManager
from agents.argus_orchestrator import ArgusOrchestrator
from thor_config import load_config

async def main():
    """Swarm management CLI"""
    parser = argparse.ArgumentParser(description="THOR Swarm Management")
    parser.add_argument("action", choices=["start", "stop", "status", "deploy", "list"])
    parser.add_argument("--agent-type", help="Agent type for deploy action")
    parser.add_argument("--all", action="store_true", help="Apply to all agents")
    
    args = parser.parse_args()
    
    config = load_config()
    swarm_manager = SwarmManager()
    argus_orchestrator = ArgusOrchestrator()
    
    try:
        if args.action == "start":
            if args.all:
                # Start orchestrator and all agents
                result = await argus_orchestrator.start_orchestrator()
                print(f"Orchestrator: {result}")
                
                for agent_type in ["business", "legal", "science", "healthcare", "financial"]:
                    result = await argus_orchestrator.start_agent(agent_type)
                    print(f"Agent {agent_type}: {result}")
            else:
                result = await argus_orchestrator.start_orchestrator()
                print(f"Orchestrator started: {result}")
        
        elif args.action == "stop":
            if args.all:
                # Stop all agents and orchestrator
                agents = await argus_orchestrator.get_agent_status()
                for agent_type in agents.get("agents", {}):
                    result = await argus_orchestrator.stop_agent(agent_type)
                    print(f"Agent {agent_type} stopped: {result}")
                
                result = await argus_orchestrator.stop_orchestrator()
                print(f"Orchestrator stopped: {result}")
            else:
                result = await argus_orchestrator.stop_orchestrator()
                print(f"Orchestrator stopped: {result}")
        
        elif args.action == "status":
            swarm_status = await swarm_manager.get_status()
            argus_status = await argus_orchestrator.get_agent_status()
            
            print("🔨 THOR Swarm Status:")
            print(f"  Swarm Manager: {swarm_status}")
            print(f"  Argus Agents: {argus_status}")
        
        elif args.action == "deploy":
            if not args.agent_type:
                print("Error: --agent-type required for deploy action")
                return 1
            
            agent_id = await swarm_manager.deploy_agent(args.agent_type)
            print(f"Agent deployed: {agent_id}")
        
        elif args.action == "list":
            agents = await swarm_manager.list_agents()
            print("🤖 Active Agents:")
            for agent in agents:
                print(f"  • {agent['agent_type']} ({agent['agent_id']}) - {agent['status']}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))