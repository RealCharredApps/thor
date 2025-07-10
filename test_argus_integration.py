# thor/test_argus_integration.py
import asyncio
import os
import sys
from pathlib import Path
import json
import subprocess

sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.thor_client import ThorClient, ThorConfig

async def locate_argus():
    """Locate Argus installation"""
    print("🔍 Locating Argus AI Agent MCPs...")
    
    # Common locations
    search_paths = [
        "./Argus_Ai_Agent_MCPs/",
        "../Argus_Ai_Agent_MCPs/",
        "../../Argus_Ai_Agent_MCPs/",
        "~/Argus_Ai_Agent_MCPs/",
        "~/Documents/GitHub/Argus_Ai_Agent_MCPs/",
        "~/Documents/GitHub/RealCharredApps/Argus_Ai_Agent_MCPs/"
    ]
    
    found_paths = []
    for path in search_paths:
        expanded_path = os.path.expanduser(path)
        if os.path.exists(expanded_path):
            found_paths.append(expanded_path)
            print(f"✅ Found Argus at: {expanded_path}")
    
    if not found_paths:
        print("❌ Argus not found in common locations")
        
        # Try to find it with system search
        print("🔍 Searching system for Argus...")
        try:
            result = subprocess.run(
                ["find", "/", "-name", "Argus_Ai_Agent_MCPs", "-type", "d", "2>/dev/null"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.stdout:
                paths = result.stdout.strip().split('\n')
                for path in paths:
                    if os.path.exists(path):
                        found_paths.append(path)
                        print(f"✅ Found Argus at: {path}")
        except:
            pass
    
    return found_paths

async def analyze_argus_structure(argus_path):
    """Analyze Argus directory structure"""
    print(f"\n📊 Analyzing Argus structure: {argus_path}")
    
    # Check for key files
    key_files = [
        "orchestrator-server.js",
        "swarm-coordinator.js",
        "business-server.js",
        "legal-server.js",
        "science-server.js",
        "healthcare-server.js", 
        "financial-server.js",
        "package.json"
    ]
    
    analysis = {
        "path": argus_path,
        "files_found": [],
        "files_missing": [],
        "directories": [],
        "package_info": None
    }
    
    # Check files
    for file in key_files:
        file_path = os.path.join(argus_path, file)
        if os.path.exists(file_path):
            analysis["files_found"].append(file)
            print(f"  ✅ {file}")
        else:
            analysis["files_missing"].append(file)
            print(f"  ❌ {file}")
    
    # List directories
    try:
        for item in os.listdir(argus_path):
            item_path = os.path.join(argus_path, item)
            if os.path.isdir(item_path):
                analysis["directories"].append(item)
    except:
        pass
    
    # Check package.json
    package_json_path = os.path.join(argus_path, "package.json")
    if os.path.exists(package_json_path):
        try:
            with open(package_json_path, 'r') as f:
                analysis["package_info"] = json.load(f)
        except:
            pass
    
    return analysis

async def test_argus_compatibility():
    """Test Argus compatibility with THOR"""
    print("\n🧪 Testing Argus compatibility...")
    
    # Find Argus
    argus_paths = await locate_argus()
    
    if not argus_paths:
        print("❌ Cannot test compatibility - Argus not found")
        return False
    
    # Use first found path
    argus_path = argus_paths[0]
    
    # Analyze structure
    analysis = await analyze_argus_structure(argus_path)
    
    # Check Node.js availability
    print("\n🟢 Checking Node.js...")
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ Node.js: {result.stdout.strip()}")
        else:
            print("  ❌ Node.js not found")
            return False
    except:
        print("  ❌ Node.js not available")
        return False
    
    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ npm: {result.stdout.strip()}")
        else:
            print("  ❌ npm not found")
    except:
        print("  ❌ npm not available")
    
    # Test basic Node.js server start (if orchestrator exists)
    orchestrator_path = os.path.join(argus_path, "orchestrator-server.js")
    if os.path.exists(orchestrator_path):
        print("\n🚀 Testing orchestrator startup...")
        try:
            # Try to start orchestrator for 5 seconds
            process = subprocess.Popen(
                ["node", "orchestrator-server.js"],
                cwd=argus_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait briefly
            await asyncio.sleep(2)
            
            # Check if still running
            if process.poll() is None:
                print("  ✅ Orchestrator starts successfully")
                process.terminate()
                process.wait()
            else:
                stdout, stderr = process.communicate()
                print(f"  ❌ Orchestrator failed to start")
                print(f"  Error: {stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ Failed to test orchestrator: {e}")
            return False
    
    return True

async def create_integration_plan(argus_paths):
    """Create integration plan"""
    print("\n📋 Creating Argus-THOR Integration Plan...")
    
    if not argus_paths:
        print("❌ No Argus installation found")
        return
    
    argus_path = argus_paths[0]
    
    plan = {
        "integration_steps": [
            "1. Copy Argus MCPs to THOR agents directory",
            "2. Update THOR configuration with Argus paths",
            "3. Create Python wrappers for Node.js servers",
            "4. Implement MCP protocol handlers",
            "5. Add Argus agents to swarm manager",
            "6. Create unified orchestration interface",
            "7. Test cross-platform communication",
            "8. Implement graceful error handling",
            "9. Add monitoring and logging",
            "10. Create documentation and examples"
        ],
        "required_changes": [
            "Update thor_config.yaml with Argus paths",
            "Enhance ArgusOrchestrator class",
            "Add MCP protocol support",
            "Create agent wrapper classes",
            "Update swarm manager for Argus agents",
            "Add Node.js process management",
            "Implement WebSocket communication",
            "Add health checks for agents"
        ],
        "compatibility_matrix": {
            "THOR Python": "3.8+",
            "Argus Node.js": "16+",
            "Communication": "HTTP/WebSocket",
            "Data Format": "JSON/MCP",
            "Process Management": "subprocess/PM2"
        }
    }
    
    # Save plan
    with open("argus_integration_plan.json", "w") as f:
        json.dump(plan, f, indent=2)
    
    print("✅ Integration plan created: argus_integration_plan.json")
    
    # Display summary
    print("\n📝 Integration Summary:")
    print(f"  • Argus Location: {argus_path}")
    print(f"  • Integration Steps: {len(plan['integration_steps'])}")
    print(f"  • Required Changes: {len(plan['required_changes'])}")
    print("  • Communication: HTTP/WebSocket + MCP Protocol")
    print("  • Process Management: Python subprocess + Node.js")

async def main():
    """Main test function"""
    print("🔨 THOR-Argus Integration Test")
    print("=" * 50)
    
    # Test basic THOR functionality
    print("🧪 Testing THOR...")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        return 1
    
    try:
        config = ThorConfig(anthropic_api_key=api_key, debug_mode=True)
        thor = ThorClient(config)
        print("✅ THOR initialized successfully")
    except Exception as e:
        print(f"❌ THOR initialization failed: {e}")
        return 1
    
    # Test Argus
    argus_paths = await locate_argus()
    compatibility = await test_argus_compatibility()
    
    if compatibility:
        print("\n✅ Argus compatibility test passed")
        await create_integration_plan(argus_paths)
    else:
        print("\n❌ Argus compatibility issues found")
        
        # Provide installation instructions
        print("\n📋 Argus Installation Instructions:")
        print("1. Clone Argus repository:")
        print("   git clone https://github.com/your-repo/Argus_Ai_Agent_MCPs.git")
        print("2. Install Node.js dependencies:")
        print("   cd Argus_Ai_Agent_MCPs && npm install")
        print("3. Test orchestrator:")
        print("   node orchestrator-server.js")
    
    return 0 if compatibility else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)