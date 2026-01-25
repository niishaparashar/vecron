import os
import sqlite3
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import os
from math import exp
from datetime import datetime

def time_decay(interacted_at, decay_rate=0.05):
    days = (datetime.now() - datetime.fromisoformat(interacted_at)).days
    return exp(-decay_rate * days)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DB_NAME = os.path.join(PROJECT_ROOT, "vecron.db")




def load_interactions():
    conn = sqlite3.connect(DB_NAME)
    interactions = pd.read_sql("""
        SELECT
        user_id,
        opportunity_id,
        interaction_weight,
        interacted_at   
        FROM interactions
        """, conn)
    conn.close()
    return interactions


def build_user_item_matrix(interactions):
    """
    rows -> users
    columns -> opportunities
    values -> interaction weights
    """
    return interactions.pivot_table(
        index="user_id",
        columns="opportunity_id",
        values ="interaction_weight",
        fill_value=0
    
    )
    
    #COMPUTING ITEM ITEM SIMILARITY
    
def compute_item_similarity(user_item_matrix):
    """
    Item-based Collaborative filtering
     """
    item_vectors = user_item_matrix.T
    similarity = cosine_similarity(item_vectors)
        
    return pd.DataFrame(
        similarity,
        index = item_vectors.index,
        columns = item_vectors.index
    )
    
def recommend_jobs_cf(user_id, top_n=5, allow_seen=False):
    interactions = load_interactions()
    ui_matrix = build_user_item_matrix(interactions)
    
    #for cold user --- first time experience
    if user_id  not in ui_matrix.index:
        return pd.DataFrame()
    
    item_similarity = compute_item_similarity(ui_matrix)
    user_vector =  ui_matrix.loc[user_id]
    interacted_jobs=  user_vector[user_vector >0].index.tolist()
    
    scores ={}
    
    for job_id in interacted_jobs:
        similar_jobs = item_similarity[job_id]
        
        for other_jobs_id, sim_score in similar_jobs.items():
            if not allow_seen and other_jobs_id in interacted_jobs:
                continue
            
    interaction_time = interactions[
    (interactions["user_id"] == user_id) &
    (interactions["opportunity_id"] == job_id)
    ]["interacted_at"].iloc[0]

    decay = time_decay(interaction_time)

    scores[other_jobs_id] = scores.get(other_jobs_id, 0) + (
    sim_score * user_vector.loc[job_id] * decay
     )

            
            
    recommendations = (
        pd.DataFrame(scores.items(), columns=["opportunity_id", "score"]).sort_values(by ="score", ascending = False).head(top_n)
    )
    return recommendations
    
    

if __name__ == "__main__":
    interactions = load_interactions()
    
    print("Interaction Sample:")
    print(interactions.head(), "\n")
    
    ui_matrix = build_user_item_matrix(interactions)
    print("User-Item Matrix shape: ", ui_matrix.shape, "\n")
    
    # Get a valid user ID
    valid_user = ui_matrix.index[0]  # 
    print(f"Testing with user: {valid_user}\n")
    
    item_similarity = compute_item_similarity(ui_matrix)
    print("Item similarity matrix computed \n")
    
    recs = recommend_jobs_cf(user_id=valid_user, top_n=5) 
    print(recs)