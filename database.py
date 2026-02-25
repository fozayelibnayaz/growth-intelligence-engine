"""
Eagle 3D Intelligence Platform - Database Module
Uses SQLite (works on Streamlit Cloud free tier)
Data persists in the app's filesystem between reruns
but resets on app restart/redeploy.
"""

import sqlite3
import hashlib
import os
import pandas as pd
from datetime import datetime

# Database file path - use /tmp for Streamlit Cloud
# or local directory for local development
DB_DIR = os.environ.get("DB_DIR", ".")
DB_PATH = os.path.join(DB_DIR, "eagle_intelligence.db")


def get_connection():
    """Get SQLite connection with WAL mode for better concurrency."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def init_database():
    """Initialize all database tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Intelligence data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intelligence_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            collection_date TEXT,
            keyword TEXT,
            question_title TEXT,
            question_body TEXT,
            answer_summary TEXT,
            proof_link TEXT,
            source TEXT,
            content_idea TEXT,
            content_outline TEXT,
            publish_recommendation TEXT,
            ai_summary TEXT,
            category TEXT,
            is_b2b BOOLEAN DEFAULT 0,
            opportunity_score REAL DEFAULT 0,
            cluster_label TEXT,
            status TEXT DEFAULT 'New',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            setting_key TEXT,
            setting_value TEXT,
            UNIQUE(user_id, setting_key)
        )
    """)

    # Daily collection logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            collection_date TEXT,
            records_collected INTEGER,
            sources TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Content tracker
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content_tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            intelligence_id INTEGER,
            content_status TEXT DEFAULT 'Planned',
            assigned_to TEXT,
            due_date TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (intelligence_id) REFERENCES intelligence_data(id)
        )
    """)

    conn.commit()
    conn.close()

    # Create default admin user if not exists
    create_user("admin", "admin123", "admin@eagle3d.com")


def _hash_password(password):
    """Hash password with SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username, password, email=""):
    """Create a new user. Returns True if successful."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
            (username, _hash_password(password), email)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Create user error: {e}")
        return False


def authenticate_user(username, password):
    """Authenticate user. Returns (id, username) tuple or None."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
            (username, _hash_password(password))
        )
        user = cursor.fetchone()
        conn.close()
        return user
    except Exception as e:
        print(f"Auth error: {e}")
        return None


def insert_intelligence_data(data_list, user_id):
    """Insert collected intelligence data into database."""
    if not data_list:
        return 0

    conn = get_connection()
    cursor = conn.cursor()
    inserted = 0

    for item in data_list:
        try:
            # Check for duplicate by proof_link and user_id
            cursor.execute(
                "SELECT id FROM intelligence_data WHERE proof_link = ? AND user_id = ?",
                (item.get('proof_link', ''), user_id)
            )
            if cursor.fetchone():
                continue

            cursor.execute("""
                INSERT INTO intelligence_data 
                (user_id, collection_date, keyword, question_title, 
                 question_body, answer_summary, proof_link, source,
                 content_idea, content_outline, publish_recommendation,
                 ai_summary, category, is_b2b, opportunity_score,
                 cluster_label, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                item.get('collection_date', ''),
                item.get('keyword', ''),
                item.get('question_title', ''),
                item.get('question_body', ''),
                item.get('answer_summary', ''),
                item.get('proof_link', ''),
                item.get('source', ''),
                item.get('content_idea', ''),
                item.get('content_outline', ''),
                item.get('publish_recommendation', ''),
                item.get('ai_summary', ''),
                item.get('category', ''),
                1 if item.get('is_b2b', False) else 0,
                item.get('opportunity_score', 0),
                item.get('cluster_label', ''),
                item.get('status', 'New'),
                item.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            ))
            inserted += 1
        except Exception as e:
            print(f"Insert error: {e}")

    conn.commit()
    conn.close()
    print(f"Database: inserted {inserted} new records")
    return inserted


def get_all_data(user_id, start_date=None, end_date=None):
    """Get all intelligence data for a user, optionally filtered by date range."""
    try:
        conn = get_connection()

        query = "SELECT * FROM intelligence_data WHERE user_id = ?"
        params = [user_id]

        if start_date:
            query += " AND collection_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND collection_date <= ?"
            params.append(end_date)

        query += " ORDER BY created_at DESC"

        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        print(f"Get all data error: {e}")
        return pd.DataFrame()


def get_data_by_date(user_id, target_date):
    """Get data for a specific date."""
    try:
        conn = get_connection()
        query = """
            SELECT * FROM intelligence_data 
            WHERE user_id = ? AND collection_date = ?
            ORDER BY opportunity_score DESC
        """
        df = pd.read_sql_query(query, conn, params=[user_id, target_date])
        conn.close()
        return df
    except Exception as e:
        print(f"Get data by date error: {e}")
        return pd.DataFrame()


def get_recent_data(user_id, days=7):
    """Get data from the last N days."""
    try:
        conn = get_connection()
        query = """
            SELECT * FROM intelligence_data 
            WHERE user_id = ? 
            AND collection_date >= date('now', ?)
            ORDER BY created_at DESC
        """
        df = pd.read_sql_query(query, conn, params=[user_id, f'-{days} days'])
        conn.close()
        return df
    except Exception as e:
        print(f"Get recent data error: {e}")
        return pd.DataFrame()


def save_setting(key, value, user_id):
    """Save a user setting."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO settings (user_id, setting_key, setting_value)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, setting_key) 
            DO UPDATE SET setting_value = excluded.setting_value
        """, (user_id, key, value))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Save setting error: {e}")


def get_setting(key, user_id):
    """Get a user setting value."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT setting_value FROM settings WHERE user_id = ? AND setting_key = ?",
            (user_id, key)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        print(f"Get setting error: {e}")
        return None


def log_daily_collection(user_id, records_count, sources, collection_date):
    """Log a daily collection run."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO daily_logs (user_id, collection_date, records_collected, sources)
            VALUES (?, ?, ?, ?)
        """, (user_id, collection_date, records_count, sources))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Log daily error: {e}")


def get_daily_logs(user_id):
    """Get daily collection logs."""
    try:
        conn = get_connection()
        query = """
            SELECT collection_date, records_collected, sources, created_at
            FROM daily_logs 
            WHERE user_id = ?
            ORDER BY collection_date DESC
            LIMIT 90
        """
        df = pd.read_sql_query(query, conn, params=[user_id])
        conn.close()
        return df
    except Exception as e:
        print(f"Get daily logs error: {e}")
        return pd.DataFrame()


def insert_content_tracker(user_id, intelligence_id, status="Planned",
                           assigned_to="", due_date="", notes=""):
    """Insert a content tracking entry."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO content_tracker 
            (user_id, intelligence_id, content_status, assigned_to, due_date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, intelligence_id, status, assigned_to, due_date, notes))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Insert content tracker error: {e}")
        return False