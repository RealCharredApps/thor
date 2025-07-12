# src/core/websocket_bridge.py - COMPLETE WORKING VERSION
import asyncio
import websockets
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.api_key_manager import APIKeyManager

class ThorWebSocketBridge:
    """Working WebSocket bridge for THOR UI"""
    
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.thor_client = None
        self.connected_clients = set()
        self.api_key_manager = APIKeyManager()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            force=True
        )
        self.logger = logging.getLogger(__name__)
    
    async def initialize_thor(self, api_key=None):
        """Initialize THOR with API key"""
        try:
            # Use provided key or load from sources
            if not api_key:
                api_key = self.api_key_manager.load_api_key()
            
            if not api_key:
                self.logger.warning("❌ No API key available")
                return False, "No API key found"
            
            # Validate API key
            is_valid, message = self.api_key_manager.validate_api_key(api_key)
            if not is_valid:
                self.logger.error(f"❌ Invalid API key: {message}")
                return False, message
            
            # Set environment variable
            os.environ['ANTHROPIC_API_KEY'] = api_key
            
            # Import and initialize THOR
            try:
                from core.thor_client import ThorClient
                self.thor_client = ThorClient()
                await self.thor_client.initialize()
                
                self.logger.info("✅ THOR backend initialized successfully")
                return True, "THOR initialized successfully"
                
            except Exception as e:
                self.logger.error(f"❌ THOR client error: {e}")
                return False, f"THOR initialization failed: {str(e)}"
            
        except Exception as e:
            error_msg = f"Initialization error: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            return False, error_msg
    
    async def handle_connection(self, websocket):
        """Handle WebSocket connections"""
        self.connected_clients.add(websocket)
        client_address = str(websocket.remote_address) if hasattr(websocket, 'remote_address') else "unknown"
        self.logger.info(f"🔌 Client connected from {client_address}")
        
        try:
            # Send initial status
            await self.send_message(websocket, {
                "type": "connection_status",
                "status": "connected",
                "thor_ready": self.thor_client is not None,
                "has_api_key": bool(self.api_key_manager.load_api_key()),
                "timestamp": datetime.now().isoformat()
            })
            
            # Listen for messages
            async for message in websocket:
                try:
                    self.logger.info(f"📥 Received message: {message[:200]}...")
                    data = json.loads(message)
                    response = await self.process_message(data)
                    await self.send_message(websocket, response)
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error: {e}")
                    await self.send_error(websocket, "Invalid JSON format")
                except Exception as e:
                    self.logger.error(f"Message processing error: {e}")
                    await self.send_error(websocket, f"Processing error: {str(e)}")
                    
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"🔌 Client {client_address} disconnected")
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
        finally:
            self.connected_clients.discard(websocket)
    
    async def process_message(self, data):
        """Process incoming messages"""
        message_type = data.get("type", "unknown")
        self.logger.info(f"🔄 Processing message type: {message_type}")
        
        try:
            if message_type == "set_api_key":
                return await self.handle_set_api_key(data)
            elif message_type == "get_api_key_status":
                return await self.handle_get_api_key_status()
            elif message_type == "chat":
                return await self.handle_chat_message(data)
            elif message_type == "tool":
                return await self.handle_tool_call(data)
            elif message_type == "cost_check":
                return await self.handle_cost_check()
            else:
                return self.create_response("error", error=f"Unknown message type: {message_type}")
                
        except Exception as e:
            self.logger.error(f"Processing error: {e}")
            return self.create_response("error", error=f"Processing failed: {str(e)}")
    
    async def handle_set_api_key(self, data):
        """Handle API key setting"""
        self.logger.info("🔑 Handling API key setup...")
        
        api_key = data.get("api_key", "").strip()
        save_to_file = data.get("save_to_file", True)
        
        if not api_key:
            return self.create_response("error", error="API key is required")
        
        # Validate API key format
        is_valid, validation_message = self.api_key_manager.validate_api_key(api_key)
        if not is_valid:
            self.logger.error(f"❌ API key validation failed: {validation_message}")
            return self.create_response("error", error=validation_message)
        
        # Save to .env file if requested
        save_success = True
        if save_to_file:
            save_success = self.api_key_manager.save_api_key(api_key)
            if not save_success:
                self.logger.error("❌ Failed to save API key to file")
                return self.create_response("error", error="Failed to save API key to .env file")
        
        # Initialize THOR with the API key
        thor_success, thor_message = await self.initialize_thor(api_key)
        
        if thor_success:
            self.logger.info("✅ API key setup completed successfully")
            return self.create_response(
                "api_key_result",
                success=True,
                message="API key saved and THOR initialized successfully",
                saved_to_file=save_success,
                thor_ready=True
            )
        else:
            self.logger.error(f"❌ THOR initialization failed: {thor_message}")
            return self.create_response(
                "api_key_result",
                success=False,
                message=f"API key saved but THOR initialization failed: {thor_message}",
                saved_to_file=save_success,
                thor_ready=False
            )
    
    async def handle_get_api_key_status(self):
        """Get API key status"""
        api_key = self.api_key_manager.load_api_key()
        
        return self.create_response(
            "api_key_status",
            has_api_key=bool(api_key),
            thor_ready=self.thor_client is not None,
            api_key_source="environment" if os.getenv('ANTHROPIC_API_KEY') else "file" if api_key else "none"
        )
    
    async def handle_chat_message(self, data):
        """Handle chat messages"""
        if not self.thor_client:
            self.logger.warning("❌ Chat attempt without THOR initialized")
            return self.create_response("error", error="THOR not initialized. Please set API key first.")
        
        session_id = data.get("session_id", "default")
        message = data.get("message", "")
        
        if not message:
            return self.create_response("error", error="Empty message")
        
        try:
            self.logger.info(f"💬 Processing chat: '{message[:50]}...'")
            
            # Process attachments if any
            attachments = data.get("attachments", [])
            processed_message = message
            
            for attachment in attachments:
                file_path = attachment.get("path", "")
                if file_path and os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        processed_message += f"\n\nFile: {file_path}\n```\n{content}\n```"
                    except Exception as e:
                        processed_message += f"\n\nError reading {file_path}: {str(e)}"
            
            # Send to THOR
            response = await self.thor_client.chat(processed_message, session_id)
            
            self.logger.info(f"✅ THOR response: '{response[:50]}...'")
            
            return self.create_response(
                "chat_response",
                session_id=session_id,
                response=response
            )
            
        except Exception as e:
            self.logger.error(f"❌ Chat processing error: {e}")
            return self.create_response("error", error=f"Chat failed: {str(e)}")
    
    async def handle_tool_call(self, data):
        """Handle tool calls"""
        if not self.thor_client:
            return self.create_response("error", error="THOR not initialized")
        
        tool_name = data.get("tool_name", "")
        tool_args = data.get("args", {})
        
        try:
            self.logger.info(f"🔧 Running tool: {tool_name}")
            
            # Tool mapping
            tool_map = {
                "list_files": self.thor_client._tool_list_files,
                "read_file": self.thor_client._tool_read_file,
                "write_file": self.thor_client._tool_write_file,
                "run_command": self.thor_client._tool_run_command,
                "analyze_code": self.thor_client._tool_analyze_code,
                "search_files": self.thor_client._tool_search_files,
                "cost_check": self.thor_client._tool_cost_check,
                "swarm_status": self.thor_client._tool_swarm_status
            }
            
            if tool_name in tool_map:
                tool_func = tool_map[tool_name]
                
                if asyncio.iscoroutinefunction(tool_func):
                    result = await tool_func(**tool_args)
                else:
                    result = tool_func(**tool_args)
                
                return self.create_response(
                    "tool_result",
                    tool_name=tool_name,
                    result=result
                )
            else:
                return self.create_response("error", error=f"Unknown tool: {tool_name}")
                
        except Exception as e:
            self.logger.error(f"❌ Tool error: {e}")
            return self.create_response("error", error=f"Tool {tool_name} failed: {str(e)}")
    
    async def handle_cost_check(self):
        """Handle cost checking"""
        if not self.thor_client:
            return self.create_response(
                "cost_update",
                daily_usage=0.0,
                daily_requests=0,
                daily_budget=0.17,
                cost_report="THOR not initialized"
            )
        
        try:
            cost_info = self.thor_client._tool_cost_check()
            usage = self.thor_client.model_selector.daily_usage
            
            return self.create_response(
                "cost_update",
                daily_usage=usage.get("cost", 0.0),
                daily_requests=usage.get("requests", 0),
                daily_budget=self.thor_client.config_manager.config.max_daily_spend,
                cost_report=cost_info
            )
            
        except Exception as e:
            self.logger.error(f"❌ Cost check error: {e}")
            return self.create_response("error", error=f"Cost check failed: {str(e)}")
    
    def create_response(self, response_type, **kwargs):
        """Create standardized response"""
        response = {
            "type": response_type,
            "timestamp": datetime.now().isoformat()
        }
        response.update(kwargs)
        return response
    
    async def send_message(self, websocket, data):
        """Send message to client"""
        try:
            message = json.dumps(data, default=str)
            await websocket.send(message)
            self.logger.info(f"📤 Sent: {data.get('type', 'unknown')}")
        except Exception as e:
            self.logger.error(f"❌ Send error: {e}")
    
    async def send_error(self, websocket, error_message):
        """Send error message"""
        await self.send_message(websocket, self.create_response("error", error=error_message))
    
    async def start_server(self):
        """Start WebSocket server"""
        self.logger.info(f"🚀 Starting THOR WebSocket server on {self.host}:{self.port}")
        
        # Try to initialize with existing API key
        existing_key = self.api_key_manager.load_api_key()
        if existing_key:
            await self.initialize_thor(existing_key)
        
        try:
            async with websockets.serve(self.handle_connection, self.host, self.port):
                self.logger.info("✅ THOR WebSocket server running and ready")
                await asyncio.Future()  # Run forever
        except Exception as e:
            self.logger.error(f"❌ Server error: {e}")
            raise

async def main():
    bridge = ThorWebSocketBridge()
    
    try:
        await bridge.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    asyncio.run(main())