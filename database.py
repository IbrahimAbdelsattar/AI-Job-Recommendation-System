import sqlite3
import json
from datetime import datetime
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "jobs.db"

def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_database():
    """Initialize the database with schema."""
    conn = get_db_connection()
    
    # Read and execute schema
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, 'r') as f:
        schema = f.read()
    
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print("✓ Database initialized successfully")

# ============= USER OPERATIONS =============

def create_user(email, password_hash, full_name=None):
    """Create a new user."""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO users (email, password_hash, full_name) VALUES (?, ?, ?)",
            (email, password_hash, full_name)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None  # Email already exists
    finally:
        conn.close()

def get_user_by_email(email):
    """Get user by email."""
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return dict(user) if user else None

def update_last_login(user_id):
    """Update user's last login timestamp."""
    conn = get_db_connection()
    conn.execute(
        "UPDATE users SET last_login = ? WHERE id = ?",
        (datetime.now(), user_id)
    )
    conn.commit()
    conn.close()



# ============= SEARCH OPERATIONS =============

def save_search(user_id, search_type, query_data, keywords):
    """Save a search query."""
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO searches (user_id, search_type, query_data, keywords) VALUES (?, ?, ?, ?)",
        (user_id, search_type, json.dumps(query_data), keywords)
    )
    conn.commit()
    search_id = cursor.lastrowid
    conn.close()
    return search_id

def get_user_searches(user_id, limit=10):
    """Get user's recent searches."""
    conn = get_db_connection()
    searches = conn.execute(
        "SELECT * FROM searches WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [dict(s) for s in searches]

# ============= JOB RESULTS =============

def save_job_results(search_id, jobs):
    """Save job results for a search."""
    conn = get_db_connection()
    
    for job in jobs:
        conn.execute(
            """INSERT INTO job_results 
               (search_id, job_title, company, location, description, skills, match_score, platform, url)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                search_id,
                job.get('title'),
                job.get('company'),
                job.get('location'),
                job.get('description'),
                json.dumps(job.get('skills', [])),
                job.get('match_score', 0),
                job.get('platform'),
                job.get('url')
            )
        )
    
    conn.commit()
    conn.close()

def get_search_results(search_id):
    """Get job results for a specific search."""
    conn = get_db_connection()
    results = conn.execute(
        "SELECT * FROM job_results WHERE search_id = ? ORDER BY match_score DESC",
        (search_id,)
    ).fetchall()
    conn.close()
    
    # Parse JSON fields
    jobs = []
    for r in results:
        job = dict(r)
        job['skills'] = json.loads(job['skills']) if job['skills'] else []
        jobs.append(job)
    
    return jobs

# ============= SAVED JOBS =============

def save_job(user_id, job_result_id, notes=None):
    """Bookmark a job."""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO saved_jobs (user_id, job_result_id, notes) VALUES (?, ?, ?)",
            (user_id, job_result_id, notes)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None  # Already saved
    finally:
        conn.close()

def get_saved_jobs(user_id):
    """Get user's saved jobs."""
    conn = get_db_connection()
    saved = conn.execute(
        """SELECT jr.*, sj.id as saved_id, sj.notes, sj.saved_at 
           FROM saved_jobs sj
           JOIN job_results jr ON sj.job_result_id = jr.id
           WHERE sj.user_id = ?
           ORDER BY sj.saved_at DESC""",
        (user_id,)
    ).fetchall()
    conn.close()
    
    jobs = []
    for r in saved:
        job = dict(r)
        job['skills'] = json.loads(job['skills']) if job['skills'] else []
        jobs.append(job)
    
    return jobs

def unsave_job(user_id, saved_job_id):
    """Remove a saved job."""
    conn = get_db_connection()
    conn.execute(
        "DELETE FROM saved_jobs WHERE id = ? AND user_id = ?",
        (saved_job_id, user_id)
    )
    conn.commit()
    conn.close()

# ============= USER PROFILE =============

def get_user_by_id(user_id):
    """Get user by ID."""
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def update_user_profile(user_id, full_name=None, email=None):
    """Update user profile information."""
    conn = get_db_connection()
    
    if full_name:
        conn.execute("UPDATE users SET full_name = ? WHERE id = ?", (full_name, user_id))
    if email:
        try:
            conn.execute("UPDATE users SET email = ? WHERE id = ?", (email, user_id))
        except sqlite3.IntegrityError:
            conn.close()
            return False  # Email already exists
    
    conn.commit()
    conn.close()
    return True

def update_user_password(user_id, new_password_hash):
    """Update user password."""
    conn = get_db_connection()
    conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_password_hash, user_id))
    conn.commit()
    conn.close()

def update_profile_photo(user_id, photo_filename):
    """Update user profile photo."""
    conn = get_db_connection()
    conn.execute("UPDATE users SET profile_photo = ? WHERE id = ?", (photo_filename, user_id))
    conn.commit()
    conn.close()
    return True

# ============= PASSWORD RESET =============

import secrets
from datetime import timedelta

def create_reset_token(email):
    """Create a password reset token for a user."""
    user = get_user_by_email(email)
    if not user:
        return None
    
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=1)  # Token valid for 1 hour
    
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)",
        (user['id'], token, expires_at)
    )
    conn.commit()
    conn.close()
    
    return token

def verify_reset_token(token):
    """Verify a password reset token and return user_id if valid."""
    conn = get_db_connection()
    result = conn.execute(
        """SELECT user_id FROM password_reset_tokens 
           WHERE token = ? AND used = 0 AND expires_at > ?""",
        (token, datetime.now())
    ).fetchone()
    conn.close()
    
    return dict(result)['user_id'] if result else None

def mark_token_used(token):
    """Mark a reset token as used."""
    conn = get_db_connection()
    conn.execute("UPDATE password_reset_tokens SET used = 1 WHERE token = ?", (token,))
    conn.commit()
    conn.close()

# Initialize database on import
if __name__ == "__main__":
    init_database()
