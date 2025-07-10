# src/core/config.py
import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

@dataclass
class ModelConfig:
    """Model configuration with cost optimization"""
    name: str
    cost_per_1k_tokens: float
    max_tokens: int
    best_for: list
    daily_limit: float = 5.0  # $5/month = ~$0.17/day

@dataclass
class ThorConfig:
    """Main THOR configuration"""
    api_key: str
    model_configs: Dict[str, ModelConfig]
    max_daily_spend: float = 0.17  # $5/month
    enable_swarm: bool = True
    argus_path: Optional[str] = None
    log_level: str = "INFO"
    chat_memory_limit: int = 50
    artifact_memory_limit: int = 100
    
class ConfigManager:
    """Advanced configuration management"""
    
    def __init__(self, config_path: str = "thor_config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.setup_logging()
        
    def load_config(self) -> ThorConfig:
        """Load configuration with defaults"""
        default_models = {
            "sonnet-4": ModelConfig(
                name="claude-3-5-sonnet-20241022",
                cost_per_1k_tokens=0.003,
                max_tokens=200000,
                best_for=["coding", "debugging", "implementation", "quick_fix", "general"]
            ),
            "opus-4": ModelConfig(
                name="claude-3-opus-20240229",
                cost_per_1k_tokens=0.015,
                max_tokens=200000,
                best_for=["architecture", "security_audit", "complex_analysis"]
            ),
            "haiku-4": ModelConfig(
                name="claude-3-haiku-20240307",
                cost_per_1k_tokens=0.00025,
                max_tokens=200000,
                best_for=["simple_tasks", "quick_responses"]
            )
        }
        
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                return ThorConfig(
                    api_key=data.get('api_key', os.getenv('ANTHROPIC_API_KEY')),
                    model_configs=default_models,
                    max_daily_spend=data.get('max_daily_spend', 0.17),
                    enable_swarm=data.get('enable_swarm', True),
                    argus_path=data.get('argus_path'),
                    log_level=data.get('log_level', 'INFO')
                )
        
        return ThorConfig(
            api_key=os.getenv('ANTHROPIC_API_KEY'),
            model_configs=default_models,
            argus_path=os.getenv('ARGUS_PATH', './Argus_Ai_Agent_MCPs')
        )
    
    def save_config(self):
        """Save current configuration"""
        with open(self.config_path, 'w') as f:
            json.dump({
                'max_daily_spend': self.config.max_daily_spend,
                'enable_swarm': self.config.enable_swarm,
                'argus_path': self.config.argus_path,
                'log_level': self.config.log_level
            }, f, indent=2)
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('thor.log'),
                logging.StreamHandler()
            ]
        )