# src/core/ui_bridge.py
import asyncio
import json
import logging
from typing import Dict, Any, Optional
import websockets
import threading
from datetime import datetime

from .thor_client import ThorClient

class ThorUIBridge:
    """Bridge between SwiftUI frontend and Python THOR backend"""
    
    def __init__(self, port: int = 8765):
        self.port = port
        self.thor_client = ThorClient()
        self.sessions = {}
        self.logger = logging.getLogger(__name__)
        
    async def start_server(self):
        """Start WebSocket server for UI communication"""
        self.logger.info(f"Starting THOR UI Bridge on port {self.port}")
        
        async def handle_client(websocket, path):
            try:
                await self.handle_ui_connection(websocket)
            except Exception as e:
                self.logger.error(f"Error handling UI connection: {e}")
        
        await websockets.serve(handle_client, "localhost", self.port)
        self.logger.info("THOR UI Bridge started successfully")
    
    async def handle_ui_connection(self, websocket):
        """Handle connection from SwiftUI frontend"""
        self.logger.info("UI connected")
        
        # Initialize THOR client
        await self.thor_client.initialize()
        
        async for message in websocket:
            try:
                data = json.loads(message)
                response = await self.process_ui_message(data)
                await websocket.send(json.dumps(response))
            except Exception as e:
                error_response = {
                    "type": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send(json.dumps(error_response))
    
    async def process_ui_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process message from UI"""
        message_type = data.get("type")
        
        if message_type == "chat":
            return await self.handle_chat_message(data)
        elif message_type == "session":
            return await self.handle_session_message(data)
        elif message_type == "tool":
            return await self.handle_tool_message(data)
        elif message_type == "settings":
            return await self.handle_settings_message(data)
        else:
            return {"type": "error", "error": f"Unknown message type: {message_type}"}
    
    async def handle_chat_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chat message from UI"""
        session_id = data.get("session_id", "default")
        message = data.get("message", "")
        attachments = data.get("attachments", [])
        
        # Process attachments
        processed_message = message
        for attachment in attachments:
            file_path = attachment.get("path")
            if file_path:
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    processed_message += f"\n\nFile: {file_path}\n```\n{content}\n```"
                except Exception as e:
                    processed_message += f"\n\nError reading file {file_path}: {e}"
        
        # Send to THOR
        response = await self.thor_client.chat(processed_message, session_id)
        
        return {
            "type": "chat_response",
            "session_id": session_id,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    
    async def handle_session_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle session management"""
        action = data.get("action")
        
        if action == "list":
            return {
                "type": "session_list",
                "sessions": list(self.sessions.keys())
            }
        elif action == "create":
            session_id = data.get("session_id", f"session_{len(self.sessions) + 1}")
            self.sessions[session_id] = {"created": datetime.now().isoformat()}
            return {
                "type": "session_created",
                "session_id": session_id
            }
        elif action == "delete":
            session_id = data.get("session_id")
            if session_id in self.sessions:
                del self.sessions[session_id]
            return {
                "type": "session_deleted",
                "session_id": session_id
            }
        
        return {"type": "error", "error": "Unknown session action"}
    
    async def handle_tool_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution"""
        tool_name = data.get("tool_name")
        tool_args = data.get("args", {})
        
        if hasattr(self.thor_client, f"_tool_{tool_name}"):
            tool_func = getattr(self.thor_client, f"_tool_{tool_name}")
            try:
                if asyncio.iscoroutinefunction(tool_func):
                    result = await tool_func(**tool_args)
                else:
                    result = tool_func(**tool_args)
                
                return {
                    "type": "tool_result",
                    "tool_name": tool_name,
                    "result": result
                }
            except Exception as e:
                return {
                    "type": "tool_error",
                    "tool_name": tool_name,
                    "error": str(e)
                }
        
        return {"type": "error", "error": f"Unknown tool: {tool_name}"}
    
    async def handle_settings_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle settings updates"""
        settings = data.get("settings", {})
        
        # Update THOR configuration
        if "api_key" in settings:
            self.thor_client.config_manager.config.api_key = settings["api_key"]
        
        if "daily_budget" in settings:
            self.thor_client.config_manager.config.max_daily_spend = settings["daily_budget"]
        
        # Save configuration
        self.thor_client.config_manager.save_config()
        
        return {
            "type": "settings_updated",
            "settings": settings
        }

def main():
    """Main entry point for UI bridge"""
    bridge = ThorUIBridge()
    
    async def run_bridge():
        await bridge.start_server()
        # Keep server running
        await asyncio.Future()
    
    asyncio.run(run_bridge())

if __name__ == "__main__":
    main()