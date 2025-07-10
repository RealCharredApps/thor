import os
from src.core.thor_client import ThorClient

# Test basic functionality
print("Testing THOR...")

try:
    client = ThorClient()
    print("✅ THOR client initialized successfully!")
    print(f"✅ Using model: {client.config['anthropic']['model']}")
    print(f"✅ API key configured: {'Yes' if client.config['anthropic']['api_key'] else 'No'}")
except Exception as e:
    print(f"❌ Error: {e}")
