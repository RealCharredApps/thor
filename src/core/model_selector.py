# src/core/model_selector.py
import time
import json
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta
import logging

class ModelSelector:
    """Intelligent model selection with cost optimization"""
    
    def __init__(self, config_manager):
        self.config = config_manager.config
        self.daily_usage = self.load_daily_usage()
        self.logger = logging.getLogger(__name__)
        
    def load_daily_usage(self) -> Dict:
        """Load daily usage tracking"""
        try:
            with open('daily_usage.json', 'r') as f:
                usage = json.load(f)
                # Reset if new day
                if usage.get('date') != datetime.now().strftime('%Y-%m-%d'):
                    usage = {'date': datetime.now().strftime('%Y-%m-%d'), 'cost': 0.0, 'requests': 0}
                return usage
        except FileNotFoundError:
            return {'date': datetime.now().strftime('%Y-%m-%d'), 'cost': 0.0, 'requests': 0}
    
    def save_daily_usage(self):
        """Save daily usage tracking"""
        with open('daily_usage.json', 'w') as f:
            json.dump(self.daily_usage, f)
    
    def choose_model(self, task: str, complexity: str = "medium") -> Tuple[str, ModelConfig]:
        """Choose optimal model based on task and budget"""
        
        # Check daily budget
        if self.daily_usage['cost'] >= self.config.max_daily_spend:
            self.logger.warning("Daily budget exceeded, using most economical model")
            return "haiku-4", self.config.model_configs["haiku-4"]
        
        # Task-based selection
        if task in ['coding', 'debugging', 'implementation', 'quick_fix']:
            if complexity == "high" and self.daily_usage['cost'] < self.config.max_daily_spend * 0.8:
                return 'opus-4', self.config.model_configs['opus-4']
            return 'sonnet-4', self.config.model_configs['sonnet-4']
        
        elif task in ['architecture', 'security_audit', 'complex_analysis']:
            return 'opus-4', self.config.model_configs['opus-4']
        
        elif task in ['simple_query', 'quick_response']:
            return 'haiku-4', self.config.model_configs['haiku-4']
        
        else:
            return 'sonnet-4', self.config.model_configs['sonnet-4']
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model_name: str) -> float:
        """Estimate cost for request"""
        model_config = self.config.model_configs[model_name]
        return (input_tokens + output_tokens) * model_config.cost_per_1k_tokens / 1000
    
    def update_usage(self, cost: float):
        """Update daily usage tracking"""
        self.daily_usage['cost'] += cost
        self.daily_usage['requests'] += 1
        self.save_daily_usage()