import sqlite3
import pandas as pd

conn = sqlite3.connect("vecron.db")
users = pd.read_sql("SELECT user_id FROM users", conn)
conn.close()

print(users.head(10))
import sqlite3
import pandas as pd

conn = sqlite3.connect("vecron.db")
users = pd.read_sql("SELECT user_id FROM users", conn)
conn.close()

print(users.head(10))


