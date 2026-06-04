import sqlite3
import os
from datetime import datetime

DB_NAME = "attendance_system.db"

def init_db():
    """Initializes the database and creates the attendance table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            name TEXT NOT NULL,
            check_in TEXT,
            check_out TEXT,
            UNIQUE(date, name)
        )
    ''')
    conn.commit()
    conn.close()

def log_attendance(name, action_type):
    """Logs check-in or check-out for the current day."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    name = name.lower().strip()

    try:
        if action_type == "check_in":
            # INSERT OR IGNORE preserves the very first check-in time of the day
            cursor.execute('''
                INSERT OR IGNORE INTO attendance (date, name, check_in)
                VALUES (?, ?, ?)
            ''', (date_str, name, time_str))
            
        elif action_type == "check_out":
            # Update the existing row for today with the latest check-out time
            cursor.execute('''
                SELECT id FROM attendance WHERE date = ? AND name = ?
            ''', (date_str, name))
            row = cursor.fetchone()
            
            if row:
                cursor.execute('''
                    UPDATE attendance SET check_out = ? WHERE date = ? AND name = ?
                ''', (time_str, date_str, name))
            else:
                cursor.execute('''
                    INSERT INTO attendance (date, name, check_out)
                    VALUES (?, ?, ?)
                ''', (date_str, name, time_str))
                
        conn.commit()
        return True, f"{action_type.replace('_', ' ').title()} recorded for {name.title()}."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_all_attendance_data():
    """Fetches all records sorted by date for the Excel export sheet."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT date, name, check_in, check_out FROM attendance ORDER BY date DESC, name ASC")
    data = cursor.fetchall()
    conn.close()
    return data

# Automatically initialize database when this module is referenced
if not os.path.exists(DB_NAME):
    init_db()