import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DB_NAME = os.path.join(PROJECT_ROOT, "vecron.db")



def extract_skills_overlap(user_skills, job_skills, max_skills=3):
    user_set = {s.strip().lower() for s in user_skills.split(",")}
    job_set = {s.strip().lower() for s in job_skills.split(",")}
    
    overlap = sorted(user_set & job_set) 
    return overlap[:max_skills] 

def load_data():
    conn= sqlite3.connect(DB_NAME)
    
    user= pd.read_sql("""SELECT 
                      user_id,
                      skills,
                      preferred_category,
                      experience_level
                      FROM users""", conn)
    
    jobs = pd.read_sql("""SELECT 
                       opportunity_id,
                       company_name,
                       title,
                       skills_required,
                       category,
                       experience_level,
                       location, 
                       workplace_type
                       FROM opportunities""", conn)
 
    conn.close()
    return user, jobs

def build_vectorizer(job_skills):
    vectorizer =TfidfVectorizer(
        lowercase=True,
        token_pattern= r"[^,]+"
    )
    job_tfidf = vectorizer.fit_transform(job_skills)
    return vectorizer, job_tfidf

def recommend_jobs_for_user(user_id, top_n=5):
    users, jobs = load_data()
    
    

    # Get user row
    user_rows = users[users["user_id"] == user_id]

    if user_rows.empty:
        print(f" user {user_id} not found")
        return pd.DataFrame()

    user = user_rows.iloc[0]
    # --- ADMIN GUARD ---
# Admin users should never get recommendations
    if "is_admin" in user and user["is_admin"] == 1:
     return pd.DataFrame()
  

    # --- FILTERING (before similarity) ---
    # Try strict filtering first
    '''filtered_jobs = jobs[
     (jobs["category"] == user  ["preferred_category"]) &
     (jobs["experience_level"] == user["experience_level"])
    ]'''
    filtered_jobs = jobs.copy()
    
    

    # Fallback if filtering is too strict
    if filtered_jobs.empty:      #<-- cold start
        filtered_jobs = jobs.copy()

    # --- VECTORIZE ---
    vectorizer, job_tfidf = build_vectorizer(filtered_jobs["skills_required"])
    user_skills = user["skills"] if isinstance(user["skills"], str) else ""
    user_vector = vectorizer.transform([user_skills])


    # --- SIMILARITY ---
    similarities = cosine_similarity(user_vector, job_tfidf)[0]

    filtered_jobs = filtered_jobs.copy()
    filtered_jobs["score"] = similarities
    
    
    #soft filtering
    filtered_jobs["score"]= similarities
     
    #category filtering
    filtered_jobs.loc[
        filtered_jobs["category"] == user["preferred_category"],
        "score"] *=1.2
    
    #experience level filtering
    filtered_jobs.loc[
        filtered_jobs["experience_level"] == user["experience_level"],
        "score"] *=1.1
    
    ## adding explanation
    explanation=[]
    for _, row in filtered_jobs.iterrows():
        overlap =  extract_skills_overlap(
            user_skills = user_skills,
            job_skills = row['skills_required']
            
        )
        if overlap:
            explanation.append("matched on " + ",".join(overlap))
        else:
            explanation.append("matched on overall skill similarity")
            
    filtered_jobs['explanation'] = explanation


    # --- SORT & RETURN ---
    recommendations = filtered_jobs.sort_values(
        by="score",
        ascending=False
    ).head(top_n)
    
    


    expected_cols =[
        "opportunity_id",
        "company_name",
        "title",
        "location",
        "workplace_type",
        "score",
        "explanation"
    ]
    
     
    
    return recommendations

if __name__ == "__main__":
    import sqlite3
    conn = sqlite3.connect(os.path.join(PROJECT_ROOT, "vecron.db"))
    first_user_id = conn.execute("SELECT user_id FROM users LIMIT 1").fetchone()[0]
    conn.close()
    
    print(f"Testing with user_id={first_user_id}")
    recs = recommend_jobs_for_user(user_id=first_user_id, top_n=5)
    print(recs)
     
