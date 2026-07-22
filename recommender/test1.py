import pandas as pd
from app.database import get_db

conn = get_db()
users = pd.read_sql("SELECT user_id FROM users", conn)
conn.close()

print(users.head(10))
