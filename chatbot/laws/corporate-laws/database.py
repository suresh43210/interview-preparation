import sqlite3
import datetime
import os

DB_PATH = "chat_logs.db"

def init_db():
    """Initialize the SQLite database for analytics tracking."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_query TEXT,
            bot_response TEXT,
            sources_used TEXT,
            model_used TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_interaction(user_query, bot_response, sources_used, model_used):
    """Log a single user interaction to the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Convert sources list to string for easy storage
        sources_str = ", ".join([f"{src['act']} ({src['section']})" for src in sources_used]) if sources_used else "No sources"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO logs (timestamp, user_query, bot_response, sources_used, model_used)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, user_query, bot_response, sources_str, model_used))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging to database: {e}")

# Initialize the DB when this module is loaded
init_db()
