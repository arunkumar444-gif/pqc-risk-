import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "pqc_analyzer.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Cryptographic Assets Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_name TEXT NOT NULL,
        environment TEXT NOT NULL,
        algorithm_name TEXT NOT NULL,
        algorithm_category TEXT NOT NULL,
        key_size TEXT NOT NULL,
        cryptographic_purpose TEXT NOT NULL,
        provenance TEXT NOT NULL,
        exposure_score REAL,
        sensitivity_score REAL,
        lifetime_score REAL,
        external_score REAL,
        criticality_score REAL,
        overall_risk_score REAL,
        risk_category TEXT,
        readiness_score REAL,
        agility_score REAL,
        priority_code TEXT,
        recommended_standard TEXT,
        rationale TEXT
    );
    """)
    
    # Users Table Creation
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        signup_time TEXT,
        preferred_language TEXT
    );
    """)
    
    # Safely migrate/add columns if updating from an older database version
    cursor.execute("PRAGMA table_info(users);")
    columns = [col[1] for col in cursor.fetchall()]
    if "signup_time" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN signup_time TEXT;")
    if "preferred_language" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN preferred_language TEXT;")
    
    # Create default admin account if not present
    cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, signup_time, preferred_language) VALUES (?, ?, ?, ?, ?)",
            ("admin", hash_password("admin123"), "Administrator", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "English")
        )
        
    conn.commit()
    conn.close()

def register_user(username, password, role="Analyst", language="English"):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, signup_time, preferred_language) VALUES (?, ?, ?, ?, ?)",
            (username, hash_password(password), role, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), language)
        )
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username, hash_password(password))
    )
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def insert_asset(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO assets (
        asset_name, environment, algorithm_name, algorithm_category, key_size,
        cryptographic_purpose, provenance, exposure_score, sensitivity_score,
        lifetime_score, external_score, criticality_score, overall_risk_score,
        risk_category, readiness_score, agility_score, priority_code,
        recommended_standard, rationale
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['asset_name'], data['environment'], data['algorithm_name'], data['algorithm_category'],
        data['key_size'], data['cryptographic_purpose'], data['provenance'], data['exposure_score'],
        data['sensitivity_score'], data['lifetime_score'], data['external_score'], data['criticality_score'],
        data['overall_risk_score'], data['risk_category'], data['readiness_score'], data['agility_score'],
        data['priority_code'], data['recommended_standard'], data['rationale']
    ))
    conn.commit()
    conn.close()

def get_all_assets():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def clear_all_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assets")
    conn.commit()
    conn.close()