# tests/test_basic.py
import pytest
import asyncio
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config import ConfigManager, ModelConfig
from core.model_selector import ModelSelector
from core.file_operations import FileOperations

def test_config_manager():
    """Test configuration management"""
    config = ConfigManager("test_config.json")
    assert config.config is not None
    assert config.config.max_daily_spend > 0
    
def test_model_config():
    """Test model configuration"""
    model = ModelConfig(
        name="claude-3-sonnet-20240229",
        cost_per_1k_tokens=0.003,
        max_tokens=100000,
        best_for=["coding", "general"]
    )
    assert model.name == "claude-3-sonnet-20240229"
    assert model.cost_per_1k_tokens == 0.003

def test_file_operations():
    """Test file operations"""
    file_ops = FileOperations()
    
    # Test directory listing
    result = file_ops.list_files(".")
    assert "📂 Contents" in result
    
    # Test file writing and reading
    test_content = "Hello, THOR!"
    write_result = file_ops.write_file("test_file.txt", test_content)
    assert "✅" in write_result
    
    read_result = file_ops.read_file("test_file.txt")
    assert read_result == test_content
    
    # Cleanup
    Path("test_file.txt").unlink(missing_ok=True)

if __name__ == "__main__":
    pytest.main([__file__])