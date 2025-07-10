# thor/src/utils/conversation_memory.py
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class ConversationMessage:
    role: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

class ConversationMemory:
    """Manages conversation memory and persistence"""
    
    def __init__(self, session_id: str, limit: int = 50):
        self.session_id = session_id
        self.limit = limit
        self.messages: List[ConversationMessage] = []
        self.memory_dir = Path("thor/memory")
        self.memory_dir.mkdir(exist_ok=True)
        
        # Load existing conversation if available
        self._load_session()
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to conversation memory"""
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.messages.append(message)
        
        # Maintain limit
        if len(self.messages) > self.limit:
            self.messages = self.messages[-self.limit:]
    
    def get_context(self, last_n: int = None) -> List[Dict[str, str]]:
        """Get conversation context for API calls"""
        messages = self.messages[-last_n:] if last_n else self.messages
        
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get conversation summary"""
        return {
            "session_id": self.session_id,
            "message_count": len(self.messages),
            "first_message": self.messages[0].timestamp.isoformat() if self.messages else None,
            "last_message": self.messages[-1].timestamp.isoformat() if self.messages else None,
            "user_messages": sum(1 for msg in self.messages if msg.role == "user"),
            "assistant_messages": sum(1 for msg in self.messages if msg.role == "assistant")
        }
    
    def save_to_file(self, filepath: str = None) -> str:
        """Save conversation to file"""
        if not filepath:
            filepath = self.memory_dir / f"{self.session_id}.json"
        
        data = {
            "session_id": self.session_id,
            "created_at": datetime.now().isoformat(),
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata
                }
                for msg in self.messages
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Conversation saved to {filepath}")
        return str(filepath)
    
    def load_from_file(self, filepath: str):
        """Load conversation from file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.session_id = data["session_id"]
            self.messages = []
            
            for msg_data in data["messages"]:
                message = ConversationMessage(
                    role=msg_data["role"],
                    content=msg_data["content"],
                    timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                    metadata=msg_data.get("metadata", {})
                )
                self.messages.append(message)
            
            logger.info(f"Conversation loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to load conversation: {str(e)}")
    
    def _load_session(self):
        """Load existing session if available"""
        session_file = self.memory_dir / f"{self.session_id}.json"
        if session_file.exists():
            self.load_from_file(str(session_file))
    
    def clear(self):
        """Clear conversation memory"""
        self.messages.clear()
        logger.info(f"Conversation memory cleared for session {self.session_id}")
    
    def export_markdown(self, filepath: str = None) -> str:
        """Export conversation to markdown format"""
        if not filepath:
            filepath = self.memory_dir / f"{self.session_id}.md"
        
        markdown_content = f"# Conversation: {self.session_id}\n\n"
        
        for msg in self.messages:
            role_header = "## User" if msg.role == "user" else "## Assistant"
            timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            markdown_content += f"{role_header}\n"
            markdown_content += f"*{timestamp}*\n\n"
            markdown_content += f"{msg.content}\n\n"
            markdown_content += "---\n\n"
        
        with open(filepath, 'w') as f:
            f.write(markdown_content)
        
        logger.info(f"Conversation exported to markdown: {filepath}")
        return str(filepath)