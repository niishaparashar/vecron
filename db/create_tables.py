import sqlite3
def create_tables():
 conn= sqlite3.connect("vecron.db")
 cursor = conn.cursor()

 cursor.execute("""
  CREATE TABLE IF NOT EXISTS users(
     user_id INTEGER PRIMARY KEY ,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
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
    location TEXT 
    workplace_type TEXT NOT NULL,
    posted_on DATE NOT NULL
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


 conn.commit()
 conn.close() 

create_tables()