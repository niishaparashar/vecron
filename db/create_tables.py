import os
import sqlite3


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "vecron.db")
DB_PATH = os.getenv("DB_PATH", DEFAULT_DB_PATH)


def _ensure_columns(conn, table_name, columns):
   cursor = conn.cursor()
   cursor.execute(f"PRAGMA table_info({table_name})")
   existing = {row[1] for row in cursor.fetchall()}

   for column_name, column_definition in columns.items():
      if column_name not in existing:
         cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")


def create_tables():
 conn= sqlite3.connect(DB_PATH)
 cursor = conn.cursor()

 cursor.execute("""
  CREATE TABLE IF NOT EXISTS users(
     user_id INTEGER PRIMARY KEY ,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin INTEGER NOT NULL DEFAULT 0,
        profile_completed INTEGER NOT NULL DEFAULT 0,
        current_status TEXT,
        education_level TEXT,
        branch TEXT,
        experience_level TEXT,
        skills TEXT,
        preferred_category TEXT,
        preferred_workplace TEXT,
        preferred_employment_type TEXT,
        preferred_location TEXT,
        joined_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
 )
""")

 cursor.execute("""
 CREATE TABLE IF NOT EXISTS opportunities(
    opportunity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    title TEXT NOT NULL,
    employment_type TEXT NOT NULL,
    experience_level TEXT NOT NULL,
    skills_required TEXT NOT NULL,
    department TEXT NOT NULL,
    category TEXT NOT NULL,
   location TEXT,
    workplace_type TEXT NOT NULL,
   posted_on DATE NOT NULL,
   career_page_url TEXT DEFAULT '',
   apply_url TEXT DEFAULT '',
   job_description TEXT DEFAULT ''
 )
 """)

 cursor.execute("""
  CREATE TABLE IF NOT EXISTS interactions(
    interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL, 
    opportunity_id INTEGER NOT NULL,
    interaction_type TEXT NOT NULL,
    interaction_weight INTEGER NOT NULL,
    interacted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(opportunity_id) REFERENCES opportunities(opportunity_id)
  )
 """)



 _ensure_columns(conn, "users", {
    "is_admin": "INTEGER NOT NULL DEFAULT 0",
    "profile_completed": "INTEGER NOT NULL DEFAULT 0",
 })

 _ensure_columns(conn, "opportunities", {
    "career_page_url": "TEXT DEFAULT ''",
    "apply_url": "TEXT DEFAULT ''",
    "job_description": "TEXT DEFAULT ''",
 })

 conn.commit()
 conn.close() 

if __name__ == "__main__":
    create_tables()