import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from config import BASE_DIR

CHAT_DB_PATH = BASE_DIR / "data" / "chats.db"

def init_database():
    """Initialize the chat database with required tables and indexes."""
    CHAT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(CHAT_DB_PATH) as conn:
        # Create chats table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create messages table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                citations TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
            )
        ''')

        # Create indexes for performance
        conn.execute('CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_chats_updated_at ON chats(updated_at)')

        # Add sources column if it doesn't exist (for backward compatibility)
        try:
            conn.execute('ALTER TABLE messages ADD COLUMN sources TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists

def create_chat(title: str) -> str:
    """Create a new chat thread and return its ID."""
    chat_id = f"chat_{int(datetime.now().timestamp() * 1000)}"

    with sqlite3.connect(CHAT_DB_PATH) as conn:
        conn.execute('''
            INSERT INTO chats (id, title)
            VALUES (?, ?)
        ''', (chat_id, title))

    return chat_id

def save_message(chat_id: str, role: str, content: str, citations: Optional[List[Dict[str, Any]]] = None, sources: Optional[List[Dict[str, Any]]] = None) -> str:
    """Save a message to the database and return its ID."""
    message_id = f"msg_{int(datetime.now().timestamp() * 1000)}"

    try:
        with sqlite3.connect(CHAT_DB_PATH) as conn:
            citations_json = json.dumps(citations) if citations else None
            sources_json = json.dumps(sources) if sources else None
            print(f"Saving message: role={role}, content_length={len(content)}, citations_present={citations is not None}, sources_present={sources is not None}")

            conn.execute('''
                INSERT INTO messages (id, chat_id, role, content, citations, sources)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (message_id, chat_id, role, content, citations_json, sources_json))

            # Update chat's updated_at timestamp
            conn.execute('''
                UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE id = ?
            ''', (chat_id,))

        print(f"Successfully saved message with ID: {message_id}")
        return message_id
    except Exception as e:
        print(f"Error saving message: {e}")
        import traceback
        traceback.print_exc()
        raise

def get_chat_list(limit: int = 50) -> List[Dict[str, Any]]:
    """Get list of chats ordered by most recent update."""
    with sqlite3.connect(CHAT_DB_PATH) as conn:
        rows = conn.execute('''
            SELECT id, title, created_at, updated_at
            FROM chats
            ORDER BY updated_at DESC
            LIMIT ?
        ''', (limit,)).fetchall()

        return [{
            'id': row[0],
            'title': row[1],
            'created_at': row[2],
            'updated_at': row[3]
        } for row in rows]

def get_chat_messages(chat_id: str) -> List[Dict[str, Any]]:
    """Get all messages for a specific chat."""
    with sqlite3.connect(CHAT_DB_PATH) as conn:
        rows = conn.execute('''
            SELECT id, role, content, citations, sources, timestamp
            FROM messages
            WHERE chat_id = ?
            ORDER BY timestamp ASC
        ''', (chat_id,)).fetchall()

        messages = []
        for row in rows:
            message = {
                'id': row[0],
                'role': row[1],
                'content': row[2],
                'timestamp': row[5]
            }
            if row[3]:  # citations
                message['citations'] = json.loads(row[3])
            if row[4]:  # sources
                message['sources'] = json.loads(row[4])
            messages.append(message)

        return messages

def delete_chat(chat_id: str) -> bool:
    """Delete a chat and all its messages."""
    with sqlite3.connect(CHAT_DB_PATH) as conn:
        cursor = conn.execute('DELETE FROM chats WHERE id = ?', (chat_id,))
        return cursor.rowcount > 0

def get_chat_title(chat_id: str) -> Optional[str]:
    """Get the title of a specific chat."""
    with sqlite3.connect(CHAT_DB_PATH) as conn:
        row = conn.execute('SELECT title FROM chats WHERE id = ?', (chat_id,)).fetchone()
        return row[0] if row else None

def update_chat_title(chat_id: str, title: str):
    """Update the title of a chat."""
    with sqlite3.connect(CHAT_DB_PATH) as conn:
        conn.execute('''
            UPDATE chats SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        ''', (title, chat_id))

# Initialize database on import
init_database()