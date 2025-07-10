# thor/src/utils/model_selector.py
import logging
from typing import Dict, List, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ModelInfo:
    name: str
    cost_per_1k_tokens: float
    max_tokens: int
    capabilities: List[str]
    use_cases: List[str]

class ModelSelector:
    """Intelligent model selection based on task requirements"""
    
    def __init__(self):
        self.models = {
            "claude-3-5-sonnet-20241022": ModelInfo(
                name="claude-3-5-sonnet-20241022",
                cost_per_1k_tokens=0.003,
                max_tokens=8192,
                capabilities=["coding", "analysis", "reasoning", "creative"],
                use_cases=["coding", "debugging", "implementation", "quick_fix", "general"]
            ),
            "claude-3-opus-20240229": ModelInfo(
                name="claude-3-opus-20240229",
                cost_per_1k_tokens=0.015,
                max_tokens=4096,
                capabilities=["complex_reasoning", "architecture", "security", "research"],
                use_cases=["architecture", "security_audit", "complex_analysis", "research"]
            ),
            "claude-3-haiku-20240307": ModelInfo(
                name="claude-3-haiku-20240307",
                cost_per_1k_tokens=0.00025,
                max_tokens=4096,
                capabilities=["simple_tasks", "quick_responses"],
                use_cases=["simple_queries", "quick_answers", "basic_tasks"]
            )
        }
        
        # Cost tracking
        self.usage_stats = {
            "total_tokens": 0,
            "total_cost": 0.0,
            "monthly_tokens": 0,
            "monthly_cost": 0.0
        }
    
    def choose_model(self, task_type: str, complexity: str = "medium") -> str:
        """Choose the most appropriate model for the task"""
        
        # Cost-conscious selection
        if task_type in ['simple_query', 'quick_answer', 'basic_task']:
            return "claude-3-haiku-20240307"
        
        # High-complexity tasks
        if task_type in ['architecture', 'security_audit', 'complex_analysis', 'research']:
            return "claude-3-opus-20240229"
        
        # Default to Sonnet for balanced performance/cost
        return "claude-3-5-sonnet-20241022"
    
    def estimate_cost(self, model_name: str, estimated_tokens: int) -> float:
        """Estimate cost for a given model and token count"""
        if model_name not in self.models:
            return 0.0
        
        model_info = self.models[model_name]
        return (estimated_tokens / 1000) * model_info.cost_per_1k_tokens
    
    def track_usage(self, model_name: str, tokens_used: int):
        """Track usage statistics"""
        if model_name in self.models:
            cost = self.estimate_cost(model_name, tokens_used)
            self.usage_stats["total_tokens"] += tokens_used
            self.usage_stats["total_cost"] += cost
            self.usage_stats["monthly_tokens"] += tokens_used
            self.usage_stats["monthly_cost"] += cost
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return self.usage_stats.copy()
    
    def reset_monthly_stats(self):
        """Reset monthly statistics"""
        self.usage_stats["monthly_tokens"] = 0
        self.usage_stats["monthly_cost"] = 0.0
    
    def is_within_budget(self, monthly_budget: float = 5.0) -> bool:
        """Check if usage is within monthly budget"""
        return self.usage_stats["monthly_cost"] <= monthly_budget