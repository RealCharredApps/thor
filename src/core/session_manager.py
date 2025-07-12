# src/core/session_manager.py
import asyncio
import json
import logging
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path
import threading
import uuid

from .thor_client import ThorClient

class SessionManager:
    """Manage multiple THOR sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, ThorClient] = {}
        self.session_metadata = {}
        self.logger = logging.getLogger(__name__)
        
    def create_session(self, session_id: Optional[str] = None) -> str:
        """Create a new THOR session"""
        if session_id is None:
            session_id = str(uuid.uuid4())[:8]
        
        if session_id in self.sessions:
            return session_id
        
        # Create new THOR client for this session
        client = ThorClient()
        self.sessions[session_id] = client
        self.session_metadata[session_id] = {
            "created": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "message_count": 0
        }
        
        self.logger.info(f"Created session: {session_id}")
        return session_id
    
    async def chat_with_session(self, session_id: str, message: str) -> str:
        """Chat with a specific session"""
        if session_id not in self.sessions:
            session_id = self.create_session(session_id)
        
        client = self.sessions[session_id]
        
        # Initialize client if needed
        if not hasattr(client, 'initialized'):
            await client.initialize()
            client.initialized = True
        
        # Update metadata
        self.session_metadata[session_id]["last_active"] = datetime.now().isoformat()
        self.session_metadata[session_id]["message_count"] += 1
        
        # Get response
        response = await client.chat(message, session_id)
        return response
    
    def list_sessions(self) -> Dict:
        """List all active sessions"""
        return {
            session_id: {
                **metadata,
                "status": "active" if session_id in self.sessions else "inactive"
            }
            for session_id, metadata in self.session_metadata.items()
        }
    
    def close_session(self, session_id: str) -> bool:
        """Close a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.logger.info(f"Closed session: {session_id}")
            return True
        return False