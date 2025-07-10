# thor/thor_config.py (Root level - simple wrapper)
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.thor_config import ThorConfig

def load_config():
    """Load THOR configuration from various sources"""
    config_paths = [
        "thor/config/thor_config.yaml",
        "thor/config/thor_config.yml",
        "thor/config/thor_config.json",
        "thor_config.yaml",
        "thor_config.yml",
        "thor_config.json",
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            return ThorConfig.from_file(config_path)
    
    # Fallback to environment variables
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("No config file found and ANTHROPIC_API_KEY not set")
    
    return ThorConfig(anthropic_api_key=api_key)

# Export for easy importing
__all__ = ["load_config", "ThorConfig"]