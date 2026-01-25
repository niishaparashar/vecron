import pandas as pd
import random
from datetime import datetime, timedelta

users = pd.read_csv("db/users.csv")
jobs = pd.read_csv("db/opportunity.csv")

random.seed(42)

INTERACTIONS = {
    "view": 1,
    "save": 3,
    "apply": 5
}

rows = []
interaction_id = 1

for user_id in users["user_id"]:
    viewed = random.sample(
        list(jobs["opportunity_id"]),
        random.randint(5, 10)
    )

    for job_id in viewed:
        rows.append([
            interaction_id,
            user_id,
            job_id,
            "view",
            INTERACTIONS["view"],
            datetime.now() - timedelta(days=random.randint(0, 30))
        ])
        interaction_id += 1

    for job_id in random.sample(viewed, random.randint(2, 4)):
        rows.append([
            interaction_id,
            user_id,
            job_id,
            "save",
            INTERACTIONS["save"],
            datetime.now() - timedelta(days=random.randint(0, 30))
        ])
        interaction_id += 1

    for job_id in random.sample(viewed, random.randint(1, 2)):
        rows.append([
            interaction_id,
            user_id,
            job_id,
            "apply",
            INTERACTIONS["apply"],
            datetime.now() - timedelta(days=random.randint(0, 30))
        ])
        interaction_id += 1

df = pd.DataFrame(rows, columns=[
    "interaction_id",
    "user_id",
    "opportunity_id",
    "interaction_type",
    "interaction_weight",
    "interacted_at"
])

df.to_csv("db/interactions.csv", index=False)

print("✅ interactions.csv regenerated using permanent user_id")
