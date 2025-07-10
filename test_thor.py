# thor/test_thor.py
import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.thor_client import ThorClient, ThorConfig

async def test_thor():
    """Test THOR functionality"""
    print("🔨 Testing THOR AI Development Assistant")
    print("=" * 50)
    
    # Load config
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        return False
    
    config = ThorConfig(
        anthropic_api_key=api_key,
        enable_swarm=False,  # Disable swarm for basic test
        debug_mode=True
    )
    
    try:
        # Initialize THOR
        thor = ThorClient(config)
        print("✅ THOR client initialized successfully")
        
        # Test basic functionality
        print("\n🧪 Testing basic functionality...")
        
        # Test file operations
        response = await thor.process_message("List files in the current directory")
        print(f"📁 File listing: {response.get('status', 'unknown')}")
        
        # Test code analysis
        response = await thor.process_message("Analyze the file test_thor.py")
        print(f"🔍 Code analysis: {response.get('status', 'unknown')}")
        
        # Test conversation memory
        response = await thor.process_message("What did I just ask you to do?")
        print(f"🧠 Memory test: {response.get('status', 'unknown')}")
        
        # Test kill switch
        await thor._tool_kill_switch({"reason": "Testing kill switch"})
        thor.reset_kill_switch()
        print("🛑 Kill switch test: OK")
        
        # Get usage stats
        stats = thor.get_usage_stats()
        print(f"📊 Usage stats: {stats}")
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_argus_connection():
    """Test Argus connection"""
    print("\n🔗 Testing Argus connection...")
    
    # Check if Argus directory exists
    argus_paths = [
        "./Argus_Ai_Agent_MCPs/",
        "../Argus_Ai_Agent_MCPs/",
        "../../Argus_Ai_Agent_MCPs/"
    ]
    
    argus_found = False
    for path in argus_paths:
        if os.path.exists(path):
            print(f"✅ Found Argus at: {path}")
            argus_found = True
            
            # List contents
            contents = os.listdir(path)
            print(f"📋 Argus contents: {contents[:10]}...")  # First 10 items
            break
    
    if not argus_found:
        print("❌ Argus not found. Need to locate or install.")
        return False
    
    print("✅ Argus connection test passed")
    return True

async def main():
    """Main test function"""
    # Test THOR
    thor_ok = await test_thor()
    
    # Test Argus
    argus_ok = await test_argus_connection()
    
    if thor_ok and argus_ok:
        print("\n🎉 All systems ready!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)