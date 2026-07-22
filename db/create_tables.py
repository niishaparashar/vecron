import os

import psycopg


def _ensure_columns(conn, table_name, columns):
   cursor = conn.cursor()
   cursor.execute(
      """
      SELECT column_name
      FROM information_schema.columns
      WHERE table_schema = current_schema() AND table_name = %s
      """,
      (table_name,),
   )
   existing = {row[0] for row in cursor.fetchall()}

   for column_name, column_definition in columns.items():
      if column_name not in existing:
         cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")


def create_tables():
 database_url = os.getenv("DATABASE_URL")
 if not database_url:
    raise RuntimeError("DATABASE_URL must be configured for PostgreSQL access")

 conn = psycopg.connect(database_url)
 cursor = conn.cursor()

 cursor.execute("""
  CREATE TABLE IF NOT EXISTS users(
     user_id SERIAL PRIMARY KEY,
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
    opportunity_id SERIAL PRIMARY KEY,
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
    interaction_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    opportunity_id INTEGER NOT NULL,
    interaction_type TEXT NOT NULL,
    interaction_weight INTEGER NOT NULL,
    interacted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(opportunity_id) REFERENCES opportunities(opportunity_id)
  )
 """)

 cursor.execute("""
  CREATE TABLE IF NOT EXISTS ingestion_logs(
    ingestion_log_id SERIAL PRIMARY KEY,
    status TEXT NOT NULL,
    received_count INTEGER NOT NULL DEFAULT 0,
    inserted_count INTEGER NOT NULL DEFAULT 0,
    updated_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
