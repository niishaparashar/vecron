import pandas as pd
import numpy as np
from recommender.hybrid import recommend_jobs_hybrid
import sqlite3

conn = sqlite3.connect("vecron.db")
interactions = pd.read_sql("SELECT * FROM interactions", conn)
conn.close()


# ---------------- CONFIG ----------------
K = 20
RANDOM_STATE = 42



print("=" * 70)
print("EVALUATION: HYBRID RECOMMENDER")
print("=" * 70)

# ---------------- TRAIN / TEST SPLIT ----------------
train_rows = []
test_rows = []

for user_id, group in interactions.groupby("user_id"):
    group = group.sample(frac=1, random_state=RANDOM_STATE)  # shuffle
    split_idx = int(0.8 * len(group))

    train_rows.append(group.iloc[:split_idx])
    test_rows.append(group.iloc[split_idx:])

train_df = pd.concat(train_rows)
test_df = pd.concat(test_rows)

print(f"Train interactions: {len(train_df)}")
print(f"Test interactions:  {len(test_df)}")

# ---------------- METRIC FUNCTIONS ----------------
def precision_recall_at_k(user_id, relevant_items, k=K):
    # Candidate set = test items ONLY
    candidates = list(relevant_items)

    if len(candidates) == 0:
        return 0.0, 0.0

    # Ask recommender to rank ONLY these candidates
    recs = recommend_jobs_hybrid(
        user_id,
        top_n=len(candidates),
        candidate_items=set(candidates)
    )

    if recs.empty:
        return 0.0, 0.0

    ranked = recs["opportunity_id"].tolist()[:k]
    relevant = set(relevant_items)

    hits = set(ranked).intersection(relevant)

    precision = len(hits) / min(k, len(ranked))
    recall = len(hits) / len(relevant)

    return precision, recall




# ---------------- EVALUATION LOOP ----------------
precisions = []
recalls = []
all_recommended_items = set()

for user_id, group in test_df.groupby("user_id"):
    relevant_jobs = group["opportunity_id"].tolist()

    p, r = precision_recall_at_k(user_id, relevant_jobs, k=K)

    precisions.append(p)
    recalls.append(r)

    recs = recommend_jobs_hybrid(user_id, top_n=K)
    if not recs.empty:
        all_recommended_items.update(recs["opportunity_id"])

# ---------------- AGGREGATE METRICS ----------------
avg_precision = np.mean(precisions)
avg_recall = np.mean(recalls)

catalog_size = interactions["opportunity_id"].nunique()
coverage = len(all_recommended_items) / catalog_size if catalog_size else 0.0

# ---------------- RESULTS ----------------
print("\n" + "=" * 70)
print("EVALUATION RESULTS")
print("=" * 70)
print(f"Average Precision@{K}: {avg_precision:.4f}")
print(f"Average Recall@{K}:    {avg_recall:.4f}")
print(f"Catalog Coverage:      {coverage:.4f}")
print("=" * 70)
