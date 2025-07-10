#!/usr/bin/env python3
import sqlite3
from pathlib import Path
from datetime import datetime

db_path = Path.home() / '.thor' / 'thor.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get recent conversations
cursor.execute('''
    SELECT role, content, timestamp 
    FROM conversations 
    ORDER BY timestamp DESC 
    LIMIT 20
''')

print("\n=== THOR CHAT HISTORY ===\n")
for role, content, timestamp in reversed(cursor.fetchall()):
    dt = datetime.fromisoformat(timestamp)
    print(f"[{dt.strftime('%H:%M:%S')}] {role.upper()}:")
    print(f"{content[:200]}..." if len(content) > 200 else content)
    print("-" * 50)

conn.close()
