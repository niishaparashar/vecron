from fastapi import APIRouter
from recommender.hybrid import recommend_jobs_hybrid
from app.database import get_db

router = APIRouter()

@router.get("/recommend/{user_id}")
def get_recommendations(user_id: int, top_n: int = 5):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT is_admin FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return {
            "user_id": user_id,
            "recommendations": [],
        }

    if row and row[0] == 1:
        return {
            "user_id": user_id,
            "recommendations": [],
        }

    recs = recommend_jobs_hybrid(user_id, top_n)

    if recs.empty:
        return {
            "user_id": user_id,
            "recommendations": []
        }

    return {
        "user_id": user_id,
        "recommendations": recs.to_dict(orient="records")
    }

    
