import sqlite3
DB_NAME="vecron.db"
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", cursor.fetchall())

conn.close()


