# thor/src/config/thor_config.py
import os
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import yaml
from pathlib import Path

@dataclass
class ThorConfig:
    """THOR Configuration"""
    
    # API Configuration
    anthropic_api_key: str
    default_model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    temperature: float = 0.7
    
    # Memory Configuration
    conversation_memory_limit: int = 50
    auto_save_conversations: bool = True
    memory_dir: str = "thor/memory"
    
    # Swarm Configuration
    enable_swarm: bool = True
    swarm_timeout: int = 300
    max_agents: int = 10
    
    # Performance Configuration
    parallel_sessions: bool = True
    max_parallel_tasks: int = 5
    kill_switch_enabled: bool = True
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "thor/logs/thor.log"
    
    # Security Configuration
    api_rate_limit: int = 100  # requests per minute
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: List[str] = field(default_factory=lambda: [
        '.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.go', '.rs', '.php',
        '.rb', '.swift', '.kt', '.scala', '.sh', '.bash', '.zsh', '.fish',
        '.html', '.css', '.scss', '.sass', '.less', '.xml', '.json', '.yaml',
        '.yml', '.toml', '.ini', '.cfg', '.conf', '.env', '.md', '.txt', '.rst',
        '.tex', '.sql', '.r', '.m', '.pl', '.lua', '.dart', '.elm', '.clj',
        '.hs', '.ml', '.fs', '.vb', '.pas', '.asm', '.s', '.dockerfile'
    ])
    
    # UI Configuration
    ui_theme: str = "dark"
    show_typing_indicators: bool = True
    auto_complete: bool = True
    
    # Budget Configuration
    monthly_budget: float = 5.0  # USD
    cost_alert_threshold: float = 0.8  # 80% of budget
    
    # Session Configuration
    session_id: Optional[str] = None
    session_timeout: int = 3600  # 1 hour
    
    @classmethod
    def from_file(cls, config_file: str) -> 'ThorConfig':
        """Load configuration from file"""
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                data = yaml.safe_load(f)
            else:
                import json
                data = json.load(f)
        
        # Override with environment variables
        for key in data:
            env_key = f"THOR_{key.upper()}"
            if env_key in os.environ:
                data[key] = os.environ[env_key]
        
        return cls(**data)
    
    def to_file(self, config_file: str):
        """Save configuration to file"""
        data = {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_')
        }
        
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        with open(config_file, 'w') as f:
            if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                yaml.dump(data, f, default_flow_style=False)
            else:
                import json
                json.dump(data, f, indent=2)
    
    def validate(self) -> List[str]:
        """Validate configuration"""
        errors = []
        
        if not self.anthropic_api_key:
            errors.append("anthropic_api_key is required")
        
        if self.max_tokens < 1:
            errors.append("max_tokens must be positive")
        
        if self.temperature < 0 or self.temperature > 1:
            errors.append("temperature must be between 0 and 1")
        
        if self.conversation_memory_limit < 1:
            errors.append("conversation_memory_limit must be positive")
        
        if self.monthly_budget < 0:
            errors.append("monthly_budget must be non-negative")
        
        return errors