import sqlite3

db_path = 'jobs.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'profile_photo' not in columns:
        print("Adding profile_photo column...")
        cursor.execute("ALTER TABLE users ADD COLUMN profile_photo TEXT")
        conn.commit()
        print("Column added successfully.")
    else:
        print("profile_photo column already exists.")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
