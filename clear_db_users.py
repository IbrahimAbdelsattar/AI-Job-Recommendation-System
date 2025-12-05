import sqlite3
import os

DB_PATH = 'jobs.db'

def clear_users():
    if not os.path.exists(DB_PATH):
        print("Database file not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check existing users
        cursor.execute("SELECT email FROM users")
        users = cursor.fetchall()
        print(f"Found {len(users)} users: {[u[0] for u in users]}")
        
        # Delete all users
        cursor.execute("DELETE FROM users")
        conn.commit()
        print("All users have been deleted from the database.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    clear_users()
