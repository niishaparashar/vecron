import pandas as pd

# Load existing users.csv (without user_id)
users = pd.read_csv("db/users.csv")

# Assign permanent user_id starting from 100
users.insert(0, "user_id", range(100, 100 + len(users)))

# Save back
users.to_csv("db/users.csv", index=False)

print("✅ users.csv regenerated with permanent user_id (starting from 100)")
print(users.head())
