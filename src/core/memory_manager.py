# src/core/memory_manager.py - CORRECTED VERSION
import json
import sqlite3
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

class MemoryManager:
    """Advanced memory management for conversations and artifacts"""
    
    def __init__(self, config_manager):
        self.config = config_manager.config
        self.db_path = Path("thor_memory.db")
        self.logger = logging.getLogger(__name__)
        self.conversation_cache = {}
        self.artifact_cache = {}
        
    async def initialize_db(self):
        """Initialize SQLite database for memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tokens INTEGER DEFAULT 0,
                cost REAL DEFAULT 0.0
            )
        """)
        
        # Artifacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                content TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def load_memory(self):
        """Load memory from database"""
        await self.initialize_db()
        
        # Load recent conversations into cache
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id, role, content, timestamp 
            FROM conversations 
            WHERE timestamp > datetime('now', '-7 days')
            ORDER BY timestamp ASC
        """)
        
        for row in cursor.fetchall():
            session_id, role, content, timestamp = row
            if session_id not in self.conversation_cache:
                self.conversation_cache[session_id] = []
            
            # Store with timestamp for internal use, but don't include in API calls
            self.conversation_cache[session_id].append({
                "role": role,
                "content": content,
                "timestamp": timestamp
            })
        
        conn.close()
    
    async def add_to_conversation(self, session_id: str, user_message: str, assistant_response: str):
        """Add conversation to memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add user message
        cursor.execute("""
            INSERT INTO conversations (session_id, role, content) 
            VALUES (?, ?, ?)
        """, (session_id, "user", user_message))
        
        # Add assistant response
        cursor.execute("""
            INSERT INTO conversations (session_id, role, content) 
            VALUES (?, ?, ?)
        """, (session_id, "assistant", assistant_response))
        
        conn.commit()
        conn.close()
        
        # Update cache
        if session_id not in self.conversation_cache:
            self.conversation_cache[session_id] = []
        
        self.conversation_cache[session_id].extend([
            {"role": "user", "content": user_message, "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": assistant_response, "timestamp": datetime.now().isoformat()}
        ])
        
        # Limit cache size
        if len(self.conversation_cache[session_id]) > self.config.chat_memory_limit:
            self.conversation_cache[session_id] = self.conversation_cache[session_id][-self.config.chat_memory_limit:]
    
    async def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for session - API compatible format"""
        if session_id not in self.conversation_cache:
            return []
        
        # Return only role and content for API compatibility
        api_messages = []
        for msg in self.conversation_cache[session_id]:
            api_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return api_messages
    
    async def save_artifact(self, name: str, content: str, category: str = "general"):
        """Save artifact with metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO artifacts (name, content, category, updated_at) 
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (name, content, category))
        
        conn.commit()
        conn.close()
        
        # Update cache
        self.artifact_cache[name] = {
            "content": content,
            "category": category,
            "updated_at": datetime.now().isoformat()
        }
    
    async def get_artifact(self, name: str) -> Optional[Dict]:
        """Get artifact by name"""
        if name in self.artifact_cache:
            return self.artifact_cache[name]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT content, category, updated_at 
            FROM artifacts 
            WHERE name = ?
        """, (name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "content": row[0],
                "category": row[1],
                "updated_at": row[2]
            }
        return None
    
    async def save_all(self):
        """Save all cached data"""
        self.logger.info("Memory saved successfully")