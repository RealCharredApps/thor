# src/core/swarm_manager.py
import asyncio
import logging
from typing import Dict, List, Optional, Any
from .argus_orchestrator import ArgusOrchestrator

class SwarmManager:
    """Advanced swarm management with coordination capabilities"""
    
    def __init__(self, config_manager):
        self.config = config_manager.config
        self.logger = logging.getLogger(__name__)
        self.orchestrator = None
        self.active_swarms = {}
        
        if self.config.enable_swarm and self.config.argus_path:
            self.orchestrator = ArgusOrchestrator(self.config.argus_path, config_manager)
    
    async def initialize_swarm(self) -> bool:
        """Initialize the swarm system"""
        if not self.orchestrator:
            self.logger.error("Swarm not enabled or Argus path not configured")
            return False
        
        success = await self.orchestrator.start_orchestrator()
        if success:
            self.logger.info("Swarm system initialized successfully")
        return success
    
    async def create_specialized_swarm(self, task_type: str, agents: List[str]) -> str:
        """Create a specialized swarm for specific task types"""
        swarm_id = f"swarm_{task_type}_{int(asyncio.get_event_loop().time())}"
        
        # Deploy requested agents
        deployed_agents = []
        for agent_type in agents:
            config = self._get_agent_config(agent_type, task_type)
            success = await self.orchestrator.deploy_agent(agent_type, config)
            if success:
                deployed_agents.append(agent_type)
        
        self.active_swarms[swarm_id] = {
            "type": task_type,
            "agents": deployed_agents,
            "status": "active",
            "created": asyncio.get_event_loop().time()
        }
        
        return swarm_id
    
    def _get_agent_config(self, agent_type: str, task_type: str) -> Dict:
        """Get configuration for specific agent type and task"""
        base_config = {
            "max_tokens": 4000,
            "temperature": 0.7,
            "task_focus": task_type
        }
        
        # Specialized configurations
        if agent_type == "legal":
            base_config.update({
                "specialization": "legal_analysis",
                "citation_required": True,
                "jurisdiction": "general"
            })
        elif agent_type == "financial":
            base_config.update({
                "specialization": "financial_analysis",
                "risk_assessment": True,
                "compliance_check": True
            })
        elif agent_type == "business":
            base_config.update({
                "specialization": "business_strategy",
                "market_analysis": True,
                "competitive_intelligence": True
            })
        
        return base_config
    
    async def execute_swarm_task(self, swarm_id: str, task: str) -> Dict:
        """Execute a task using the specified swarm"""
        if swarm_id not in self.active_swarms:
            return {"error": "Swarm not found"}
        
        swarm = self.active_swarms[swarm_id]
        result = await self.orchestrator.orchestrate_swarm(task, swarm["agents"])
        
        return {
            "swarm_id": swarm_id,
            "task": task,
            "result": result,
            "agents_used": swarm["agents"]
        }
    
    async def get_swarm_recommendations(self, task: str) -> List[str]:
        """Get recommended agents for a task"""
        recommendations = []
        
        # Task analysis for agent selection
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["legal", "contract", "law", "compliance", "regulation"]):
            recommendations.append("legal")
        
        if any(word in task_lower for word in ["financial", "budget", "investment", "cost", "profit"]):
            recommendations.append("financial")
        
        if any(word in task_lower for word in ["business", "strategy", "market", "competition"]):
            recommendations.append("business")
        
        if any(word in task_lower for word in ["research", "analysis", "scientific", "data"]):
            recommendations.append("science")
        
        if any(word in task_lower for word in ["health", "medical", "clinical", "patient"]):
            recommendations.append("healthcare")
        
        return recommendations if recommendations else ["business"]  # Default fallback