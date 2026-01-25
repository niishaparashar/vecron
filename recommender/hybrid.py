import pandas as pd
from recommender.content_based import recommend_jobs_for_user as cb_recommend
from recommender.collaborative import recommend_jobs_cf as cf_recommend
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DB_NAME = os.path.join(PROJECT_ROOT, "vecron.db")


def recommend_jobs_hybrid(user_id, top_n=5, candidate_items=None):
    print("=====HYRBRID CALLED FOR USER=====", user_id)

    # ---------- Content-based ----------
    if candidate_items is not None:
        cb_results = cb_recommend(user_id, top_n=1000)
    else:
        cb_results = cb_recommend(user_id, top_n=top_n * 3)

    if cb_results.empty:
        return pd.DataFrame()

    cb_results = cb_results.copy()

    if "similarity_score" in cb_results.columns:
        cb_results = cb_results.rename(columns={"similarity_score": "score"})

    cb_results["cb_score"] = cb_results["score"]

    # ---------- Collaborative ----------
    cf_results = cf_recommend(user_id, top_n=top_n * 3, allow_seen=True)

    if not cf_results.empty and "score" in cf_results.columns:
        cf_results = cf_results.copy()
        cf_results["cf_score"] = cf_results["score"] / cf_results["score"].max()
    else:
        cf_results = pd.DataFrame(columns=["opportunity_id", "cf_score"])

    # ---------- Merge ----------
    hybrid = cb_results.merge(
        cf_results[["opportunity_id", "cf_score"]],
        on="opportunity_id",
        how="left"
    )

    hybrid["cf_score"] = hybrid["cf_score"].fillna(0.0)

    hybrid["final_score"] = (
        0.7 * hybrid["cb_score"] +
        0.3 * hybrid["cf_score"]
    )
    # Penalize weak recommendations (negative feedback simulation)
    hybrid["final_score"] = hybrid["final_score"]- (hybrid.groupby("title").cumcount()*0.5)
    hybrid = hybrid.sort_values("final_score", ascending = False)
    return hybrid.head(top_n)
    hybrid= apply_interaction_boost(hybrid, user_id)

import sqlite3

def apply_interaction_boost(hybrid_df, user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT opportunity_id, SUM(interaction_weight) as w
        FROM interactions
        WHERE user_id = ?
        GROUP BY opportunity_id
    """, (user_id,))

    interacted = cursor.fetchall()
    conn.close()

    if not interacted:
        hybrid_df["interaction_boost"] = 0
        return hybrid_df

    interacted_ids = [row["opportunity_id"] for row in interacted]

    # BOOST SIMILAR JOBS, NOT SAME JOB
    hybrid_df["interaction_boost"] = hybrid_df["opportunity_id"].apply(
        lambda x: 1 if x in interacted_ids else 0
    )

    hybrid_df["final_score"] += 0.15 * hybrid_df["interaction_boost"]
    return hybrid_df
    
    #---------------EXPLAINABILITY
    def explain(row):


        reasons = []
        if row["cb_score"] > 0.3:
         reasons.append("Matches your skills")
        if row["cf_score"] > 0:
         reasons.append("Popular among similar users")
        if not reasons:
         reasons.append("Recommended based on overall relevance")
        return " | ".join(reasons)
    hybrid["explanation"] = hybrid.apply(explain, axis=1)


    if candidate_items is not None:
        hybrid = hybrid[hybrid["opportunity_id"].isin(candidate_items)]

    hybrid["source"] = hybrid["cf_score"].apply(
        lambda x: "hybrid" if x > 0 else "content-based"
    )

   

    if candidate_items is not None:
        return hybrid.head(len(candidate_items))
     
    ranked = hybrid.sort_values("final_score", ascending=False)

    seen_titles = set()
    diverse_rows = []

    for _, row in ranked.iterrows():
     title = row["title"].lower()

     if title in seen_titles:
      continue

     diverse_rows.append(row)
     seen_titles.add(title)

     if len(diverse_rows) == top_n:
      break

    return pd.DataFrame(diverse_rows)
    






# ============================================================
# MANUAL TEST (SAFE)
# ============================================================
if __name__ == "__main__":
    test_users = [100, 101, 102, 103, 104]  # change IDs manually

    for user_id in test_users:
        print("\n" + "=" * 70)
        print(f"Testing user_id = {user_id}")
        print("=" * 70)

        recs = recommend_jobs_hybrid(user_id=user_id, top_n=5)

        if recs.empty:
            print("No recommendations generated.")
            continue

        display_cols = [
            "opportunity_id",
            "company_name",
            "title",
            "final_score",
            "cb_score",
            "cf_score",
            "source",
            "explanation"
        ]

        available = [c for c in display_cols if c in recs.columns]
        print(recs[available].to_string(index=False))


    

