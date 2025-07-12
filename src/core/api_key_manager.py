# src/core/api_key_manager.py
import os
from pathlib import Path
import logging

class APIKeyManager:
    """Manage API key with .env file support"""
    
    def __init__(self, thor_root_path=None):
        if thor_root_path:
            self.thor_root = Path(thor_root_path)
        else:
            # Find THOR root by looking for setup.py or requirements.txt
            current = Path(__file__).parent
            while current.parent != current:
                if (current / "setup.py").exists() or (current / "requirements.txt").exists():
                    self.thor_root = current
                    break
                current = current.parent
            else:
                self.thor_root = Path(__file__).parent.parent.parent
        
        self.env_file = self.thor_root / ".env"
        self.logger = logging.getLogger(__name__)
        
    def load_api_key(self):
        """Load API key from multiple sources"""
        # 1. Environment variable (highest priority)
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if api_key and api_key.strip():
            self.logger.info("✅ API key loaded from environment variable")
            return api_key.strip()
        
        # 2. .env file
        api_key = self.load_from_env_file()
        if api_key:
            self.logger.info("✅ API key loaded from .env file")
            os.environ['ANTHROPIC_API_KEY'] = api_key  # Set in environment
            return api_key
        
        self.logger.warning("❌ No API key found")
        return None
    
    def load_from_env_file(self):
        """Load from .env file"""
        try:
            if self.env_file.exists():
                with open(self.env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('ANTHROPIC_API_KEY='):
                            key = line.split('=', 1)[1].strip().strip('"\'')
                            if key:
                                return key
        except Exception as e:
            self.logger.error(f"Error reading .env file: {e}")
        return None
    
    def save_api_key(self, api_key):
        """Save API key to .env file"""
        try:
            if not api_key or not api_key.strip():
                return False
                
            api_key = api_key.strip()
            
            # Create .env file or update existing
            env_content = []
            if self.env_file.exists():
                with open(self.env_file, 'r') as f:
                    env_content = f.readlines()
            
            # Remove existing ANTHROPIC_API_KEY line
            env_content = [line for line in env_content if not line.strip().startswith('ANTHROPIC_API_KEY=')]
            
            # Add new API key
            env_content.append(f'ANTHROPIC_API_KEY={api_key}\n')
            
            # Write back to file
            with open(self.env_file, 'w') as f:
                f.writelines(env_content)
            
            # Set in current environment
            os.environ['ANTHROPIC_API_KEY'] = api_key
            
            self.logger.info(f"✅ API key saved to {self.env_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving API key: {e}")
            return False
    
    def validate_api_key(self, api_key):
        """Validate API key format"""
        if not api_key or not api_key.strip():
            return False, "API key is required"
        
        api_key = api_key.strip()
        
        if not api_key.startswith('sk-ant-api03-'):
            return False, "API key should start with 'sk-ant-api03-'"
        
        if len(api_key) < 50:
            return False, "API key appears to be too short"
        
        return True, "API key format is valid"