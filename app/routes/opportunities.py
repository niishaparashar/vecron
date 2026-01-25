from fastapi import APIRouter
from app.database import get_db

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])

@router.get("/all")
def get_all_opportunities():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            opportunity_id,
            title,
            company_name,
            location,
            experience_level,
            workplace_type,
            skills_required,
            department,
            posted_on
        FROM opportunities 
        ORDER BY posted_on DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()

    # Convert SQLite Row objects to dicts
    opportunities = [dict(row) for row in rows]
    
    return {"opportunities": opportunities}