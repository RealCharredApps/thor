# thor/src/agents/argus_orchestrator.py
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import subprocess
import os
from dataclasses import dataclass
import signal
import psutil

logger = logging.getLogger(__name__)

@dataclass
class ArgusAgent:
    """Argus agent configuration"""
    name: str
    type: str
    port: int
    script_path: str
    process: Optional[subprocess.Popen] = None
    status: str = "stopped"
    capabilities: List[str] = None

class ArgusOrchestrator:
    """Orchestrates Argus MCP agents"""
    
    def __init__(self, argus_path: str = None):
        self.argus_path = argus_path or self._find_argus_path()
        self.agents: Dict[str, ArgusAgent] = {}
        self.base_port = 8000
        self.running = False
        
        # Define available Argus agents
        self.agent_configs = {
            "business": ArgusAgent(
                name="business",
                type="business",
                port=8001,
                script_path="business-server.js",
                capabilities=["market_analysis", "business_planning", "competitor_analysis"]
            ),
            "legal": ArgusAgent(
                name="legal",
                type="legal",
                port=8002,
                script_path="legal-server.js",
                capabilities=["contract_review", "legal_research", "compliance_check"]
            ),
            "science": ArgusAgent(
                name="science",
                type="science",
                port=8003,
                script_path="science-server.js",
                capabilities=["research", "data_analysis", "hypothesis_testing"]
            ),
            "healthcare": ArgusAgent(
                name="healthcare",
                type="healthcare",
                port=8004,
                script_path="healthcare-server.js",
                capabilities=["medical_research", "health_analytics", "diagnosis_support"]
            ),
            "financial": ArgusAgent(
                name="financial",
                type="financial",
                port=8005,
                script_path="financial-server.js",
                capabilities=["financial_analysis", "investment_advice", "risk_assessment"]
            )
        }
        
        logger.info(f"ArgusOrchestrator initialized with path: {self.argus_path}")
    
    def _find_argus_path(self) -> str:
        """Find Argus installation path"""
        possible_paths = [
            "./Argus_Ai_Agent_MCPs/",
            "../Argus_Ai_Agent_MCPs/",
            "../../Argus_Ai_Agent_MCPs/",
            os.path.expanduser("~/Argus_Ai_Agent_MCPs/")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return os.path.abspath(path)
        
        raise FileNotFoundError("Argus MCP directory not found")
    
    async def start_orchestrator(self) -> Dict[str, Any]:
        """Start the Argus orchestrator server"""
        try:
            orchestrator_script = os.path.join(self.argus_path, "orchestrator-server.js")
            
            if not os.path.exists(orchestrator_script):
                return {"error": f"Orchestrator script not found: {orchestrator_script}"}
            
            # Start orchestrator server
            process = subprocess.Popen(
                ["node", orchestrator_script],
                cwd=self.argus_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.orchestrator_process = process
            self.running = True
            
            # Wait a moment for startup
            await asyncio.sleep(2)
            
            if process.poll() is None:
                logger.info("Argus orchestrator started successfully")
                return {
                    "success": True,
                    "pid": process.pid,
                    "status": "running"
                }
            else:
                stdout, stderr = process.communicate()
                return {
                    "error": "Orchestrator failed to start",
                    "stdout": stdout,
                    "stderr": stderr
                }
                
        except Exception as e:
            logger.error(f"Failed to start orchestrator: {str(e)}")
            return {"error": str(e)}
    
    async def start_agent(self, agent_type: str) -> Dict[str, Any]:
        """Start a specific Argus agent"""
        if agent_type not in self.agent_configs:
            return {"error": f"Unknown agent type: {agent_type}"}
        
        if agent_type in self.agents and self.agents[agent_type].status == "running":
            return {"error": f"Agent {agent_type} already running"}
        
        try:
            agent_config = self.agent_configs[agent_type]
            script_path = os.path.join(self.argus_path, agent_config.script_path)
            
            if not os.path.exists(script_path):
                return {"error": f"Agent script not found: {script_path}"}
            
            # Start agent process
            process = subprocess.Popen(
                ["node", script_path],
                cwd=self.argus_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ, "PORT": str(agent_config.port)}
            )
            
            # Update agent info
            agent_config.process = process
            agent_config.status = "starting"
            self.agents[agent_type] = agent_config
            
            # Wait for startup
            await asyncio.sleep(2)
            
            if process.poll() is None:
                agent_config.status = "running"
                logger.info(f"Argus agent {agent_type} started on port {agent_config.port}")
                return {
                    "success": True,
                    "agent_type": agent_type,
                    "port": agent_config.port,
                    "pid": process.pid,
                    "status": "running"
                }
            else:
                stdout, stderr = process.communicate()
                agent_config.status = "error"
                return {
                    "error": f"Agent {agent_type} failed to start",
                    "stdout": stdout,
                    "stderr": stderr
                }
                
        except Exception as e:
            logger.error(f"Failed to start agent {agent_type}: {str(e)}")
            return {"error": str(e)}
    
    async def stop_agent(self, agent_type: str) -> Dict[str, Any]:
        """Stop a specific Argus agent"""
        if agent_type not in self.agents:
            return {"error": f"Agent {agent_type} not found"}
        
        agent = self.agents[agent_type]
        
        try:
            if agent.process and agent.process.poll() is None:
                # Try graceful shutdown first
                agent.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    agent.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    agent.process.kill()
                    agent.process.wait()
                
                agent.status = "stopped"
                logger.info(f"Argus agent {agent_type} stopped")
                
                return {
                    "success": True,
                    "agent_type": agent_type,
                    "status": "stopped"
                }
            else:
                return {"error": f"Agent {agent_type} not running"}
                
        except Exception as e:
            logger.error(f"Failed to stop agent {agent_type}: {str(e)}")
            return {"error": str(e)}
    
    async def stop_orchestrator(self) -> Dict[str, Any]:
        """Stop the Argus orchestrator"""
        try:
            if hasattr(self, 'orchestrator_process') and self.orchestrator_process:
                self.orchestrator_process.terminate()
                self.orchestrator_process.wait(timeout=5)
                self.running = False
                logger.info("Argus orchestrator stopped")
                return {"success": True, "status": "stopped"}
            else:
                return {"error": "Orchestrator not running"}
        except Exception as e:
            logger.error(f"Failed to stop orchestrator: {str(e)}")
            return {"error": str(e)}
    
    async def get_agent_status(self, agent_type: str = None) -> Dict[str, Any]:
        """Get status of specific agent or all agents"""
        if agent_type:
            if agent_type not in self.agents:
                return {"error": f"Agent {agent_type} not found"}
            
            agent = self.agents[agent_type]
            return {
                "agent_type": agent_type,
                "status": agent.status,
                "port": agent.port,
                "capabilities": agent.capabilities,
                "pid": agent.process.pid if agent.process else None
            }
        else:
            # Return status of all agents
            status = {}
            for agent_type, agent in self.agents.items():
                status[agent_type] = {
                    "status": agent.status,
                    "port": agent.port,
                    "capabilities": agent.capabilities,
                    "pid": agent.process.pid if agent.process else None
                }
            
            return {
                "orchestrator_running": self.running,
                "agents": status
            }
    
    async def execute_task(self, task: str, agent_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a task on a specific agent"""
        if agent_type not in self.agents:
            return {"error": f"Agent {agent_type} not available"}
        
        agent = self.agents[agent_type]
        
        if agent.status != "running":
            return {"error": f"Agent {agent_type} not running"}
        
        try:
            # In a real implementation, this would make HTTP requests to the agent
            # For now, simulate the execution
            await asyncio.sleep(0.5)  # Simulate processing time
            
            return {
                "success": True,
                "agent_type": agent_type,
                "task": task,
                "result": f"Task executed by {agent_type} agent: {task}",
                "capabilities_used": agent.capabilities[:2] if agent.capabilities else []
            }
            
        except Exception as e:
            logger.error(f"Task execution failed on {agent_type}: {str(e)}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all agents"""
        health_status = {
            "orchestrator": "running" if self.running else "stopped",
            "agents": {}
        }
        
        for agent_type, agent in self.agents.items():
            if agent.process and agent.process.poll() is None:
                health_status["agents"][agent_type] = "healthy"
            else:
                health_status["agents"][agent_type] = "unhealthy"
        
        return health_status
    
    async def restart_agent(self, agent_type: str) -> Dict[str, Any]:
        """Restart a specific agent"""
        # Stop the agent first
        stop_result = await self.stop_agent(agent_type)
        if not stop_result.get("success"):
            return stop_result
        
        # Wait a moment
        await asyncio.sleep(1)
        
        # Start the agent again
        return await self.start_agent(agent_type)
    
    def shutdown(self):
        """Shutdown all agents and orchestrator"""
        logger.info("Shutting down Argus orchestrator...")
        
        # Stop all agents
        for agent_type in list(self.agents.keys()):
            asyncio.create_task(self.stop_agent(agent_type))
        
        # Stop orchestrator
        if hasattr(self, 'orchestrator_process') and self.orchestrator_process:
            try:
                self.orchestrator_process.terminate()
                self.orchestrator_process.wait(timeout=5)
            except:
                try:
                    self.orchestrator_process.kill()
                except:
                    pass
        
        self.running = False
        logger.info("Argus orchestrator shutdown complete")