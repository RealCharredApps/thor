# thor/src/core/swarm_manager.py
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import uuid
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)

class CoordinationMode(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"

class AgentStatus(Enum):
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"

@dataclass
class AgentInfo:
    agent_id: str
    agent_type: str
    status: AgentStatus
    created_at: datetime
    last_active: datetime
    capabilities: List[str]
    config: Dict[str, Any]
    metrics: Dict[str, Any]

@dataclass
class SwarmTask:
    task_id: str
    description: str
    agents: List[str]
    coordination_mode: CoordinationMode
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SwarmManager:
    """Manages AI agent swarms and coordination"""
    
    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self.tasks: Dict[str, SwarmTask] = {}
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.lock = threading.Lock()
        
        # Agent type capabilities mapping
        self.agent_capabilities = {
            "business": ["market_analysis", "strategy", "planning", "financial_modeling"],
            "legal": ["contract_review", "compliance", "risk_assessment", "legal_research"],
            "science": ["research", "data_analysis", "hypothesis_testing", "technical_writing"],
            "healthcare": ["medical_research", "diagnosis_support", "treatment_planning", "health_analytics"],
            "financial": ["financial_analysis", "investment_advice", "risk_management", "accounting"],
            "technical": ["software_development", "system_design", "debugging", "code_review"],
            "creative": ["content_creation", "design", "brainstorming", "storytelling"]
        }
        
        logger.info("SwarmManager initialized")
    
    async def deploy_agent(self, agent_type: str, config: Dict[str, Any] = None) -> str:
        """Deploy a new agent"""
        if agent_type not in self.agent_capabilities:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_id = str(uuid.uuid4())
        config = config or {}
        
        agent_info = AgentInfo(
            agent_id=agent_id,
            agent_type=agent_type,
            status=AgentStatus.IDLE,
            created_at=datetime.now(),
            last_active=datetime.now(),
            capabilities=self.agent_capabilities[agent_type],
            config=config,
            metrics={"tasks_completed": 0, "success_rate": 0.0}
        )
        
        with self.lock:
            self.agents[agent_id] = agent_info
        
        logger.info(f"Agent deployed: {agent_id} ({agent_type})")
        return agent_id
    
    async def orchestrate_task(self, task: str, agents: List[str], mode: str = "sequential") -> Dict[str, Any]:
        """Orchestrate a task across multiple agents"""
        task_id = str(uuid.uuid4())
        coordination_mode = CoordinationMode(mode)
        
        # Validate agents
        available_agents = []
        for agent_type in agents:
            agent_id = await self._get_available_agent(agent_type)
            if agent_id:
                available_agents.append(agent_id)
            else:
                # Deploy new agent if needed
                agent_id = await self.deploy_agent(agent_type)
                available_agents.append(agent_id)
        
        # Create task
        swarm_task = SwarmTask(
            task_id=task_id,
            description=task,
            agents=available_agents,
            coordination_mode=coordination_mode,
            status="pending",
            created_at=datetime.now()
        )
        
        with self.lock:
            self.tasks[task_id] = swarm_task
        
        # Execute task based on coordination mode
        try:
            if coordination_mode == CoordinationMode.SEQUENTIAL:
                results = await self._execute_sequential(swarm_task)
            elif coordination_mode == CoordinationMode.PARALLEL:
                results = await self._execute_parallel(swarm_task)
            else:  # HIERARCHICAL
                results = await self._execute_hierarchical(swarm_task)
            
            swarm_task.status = "completed"
            swarm_task.completed_at = datetime.now()
            swarm_task.results = results
            
            return {
                "task_id": task_id,
                "status": "completed",
                "results": results,
                "agents_used": len(available_agents)
            }
            
        except Exception as e:
            swarm_task.status = "error"
            swarm_task.error = str(e)
            logger.error(f"Task orchestration failed: {task_id} - {str(e)}")
            
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(e)
            }
    
    async def _get_available_agent(self, agent_type: str) -> Optional[str]:
        """Get an available agent of the specified type"""
        with self.lock:
            for agent_id, agent_info in self.agents.items():
                if (agent_info.agent_type == agent_type and 
                    agent_info.status == AgentStatus.IDLE):
                    return agent_id
        return None
    
    async def _execute_sequential(self, task: SwarmTask) -> Dict[str, Any]:
        """Execute task sequentially across agents"""
        results = []
        current_input = task.description
        
        for agent_id in task.agents:
            agent_info = self.agents[agent_id]
            
            # Update agent status
            agent_info.status = AgentStatus.ACTIVE
            agent_info.last_active = datetime.now()
            
            try:
                # Execute task on agent
                result = await self._execute_on_agent(agent_id, current_input)
                results.append({
                    "agent_id": agent_id,
                    "agent_type": agent_info.agent_type,
                    "result": result,
                    "success": True
                })
                
                # Use output as input for next agent
                current_input = result.get("output", current_input)
                
                # Update metrics
                agent_info.metrics["tasks_completed"] += 1
                
            except Exception as e:
                results.append({
                    "agent_id": agent_id,
                    "agent_type": agent_info.agent_type,
                    "error": str(e),
                    "success": False
                })
                logger.error(f"Agent execution failed: {agent_id} - {str(e)}")
            
            finally:
                agent_info.status = AgentStatus.IDLE
        
        return {
            "mode": "sequential",
            "results": results,
            "final_output": current_input
        }
    
    async def _execute_parallel(self, task: SwarmTask) -> Dict[str, Any]:
        """Execute task in parallel across agents"""
        async def execute_agent(agent_id: str):
            agent_info = self.agents[agent_id]
            agent_info.status = AgentStatus.ACTIVE
            agent_info.last_active = datetime.now()
            
            try:
                result = await self._execute_on_agent(agent_id, task.description)
                agent_info.metrics["tasks_completed"] += 1
                return {
                    "agent_id": agent_id,
                    "agent_type": agent_info.agent_type,
                    "result": result,
                    "success": True
                }
            except Exception as e:
                logger.error(f"Agent execution failed: {agent_id} - {str(e)}")
                return {
                    "agent_id": agent_id,
                    "agent_type": agent_info.agent_type,
                    "error": str(e),
                    "success": False
                }
            finally:
                agent_info.status = AgentStatus.IDLE
        
        # Execute all agents in parallel
        tasks = [execute_agent(agent_id) for agent_id in task.agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "mode": "parallel",
            "results": results,
            "agents_count": len(task.agents)
        }
    
    async def _execute_hierarchical(self, task: SwarmTask) -> Dict[str, Any]:
        """Execute task hierarchically with coordination"""
        # Implement hierarchical coordination logic
        # For now, use sequential with coordination
        return await self._execute_sequential(task)
    
    async def _execute_on_agent(self, agent_id: str, input_data: str) -> Dict[str, Any]:
        """Execute task on specific agent"""
        agent_info = self.agents[agent_id]
        
        # Simulate agent execution
        # In real implementation, this would call the actual agent
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            "agent_id": agent_id,
            "agent_type": agent_info.agent_type,
            "input": input_data,
            "output": f"Processed by {agent_info.agent_type} agent: {input_data[:100]}...",
            "capabilities_used": agent_info.capabilities[:2],  # First 2 capabilities
            "processing_time": 0.1
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get swarm status"""
        with self.lock:
            agent_status = {}
            for status in AgentStatus:
                agent_status[status.value] = sum(
                    1 for agent in self.agents.values() 
                    if agent.status == status
                )
            
            task_status = {}
            for task in self.tasks.values():
                task_status[task.status] = task_status.get(task.status, 0) + 1
            
            return {
                "agents": {
                    "total": len(self.agents),
                    "by_status": agent_status,
                    "by_type": {
                        agent_type: sum(
                            1 for agent in self.agents.values() 
                            if agent.agent_type == agent_type
                        )
                        for agent_type in self.agent_capabilities.keys()
                    }
                },
                "tasks": {
                    "total": len(self.tasks),
                    "by_status": task_status
                },
                "uptime": datetime.now().isoformat()
            }
    
    async def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent"""
        with self.lock:
            if agent_id in self.agents:
                del self.agents[agent_id]
                logger.info(f"Agent removed: {agent_id}")
                return True
            return False
    
    async def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent information"""
        with self.lock:
            if agent_id in self.agents:
                return asdict(self.agents[agent_id])
            return None
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents"""
        with self.lock:
            return [asdict(agent) for agent in self.agents.values()]
    
    async def get_task_info(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task information"""
        with self.lock:
            if task_id in self.tasks:
                return asdict(self.tasks[task_id])
            return None
    
    def shutdown(self):
        """Shutdown swarm manager"""
        self.executor.shutdown(wait=True)
        logger.info("SwarmManager shutdown complete")