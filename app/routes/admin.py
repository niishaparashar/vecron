from fastapi import APIRouter
from app.database import get_db
from datetime import date


router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/analytics")
def get_admin_insights():
    conn = get_db()
    cursor = conn.cursor()

    # Total users
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    # Users registered today
    cursor.execute("""
        SELECT COUNT(*) 
        FROM users 
        WHERE joined_on >=  date('now', 'localtime')
    """)
    registered_today = cursor.fetchone()[0]

    # Total interactions
    cursor.execute("SELECT COUNT(*) FROM interactions")
    total_interactions = cursor.fetchone()[0]

    # Top skills (simple frequency)
    cursor.execute("SELECT skills FROM users WHERE skills IS NOT NULL")
    rows = cursor.fetchall()

    from collections import Counter

    skill_counter = Counter()

    for (skills,) in rows:
       for skill in skills.split(","):
        skill_counter[skill.strip().lower()] += 1

    
    top_skill = [
    {"skill": skill.title(), "count": count}
    for skill, count in skill_counter.most_common(5)
]

    



    conn.close()

    return {
        "total_users": total_users,
        "registered_today": registered_today,
        "total_interactions": total_interactions,
        "top_skills": top_skill

    }


@router.get("/users")
def recent_users(limit: int | None=None):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, full_name, email, experience_level, skills, preferred_location, joined_on
        FROM users
        ORDER BY joined_on IS NULL, joined_on DESC
        LIMIT ?          
        
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return {
        "users": [
            {
                "user_id": r[0],
                "full_name": r[1],
                "email": r[2],
                "experience_level": r[3],
                "skills": r[4],
                "preferred_location": r[5],
                "joined_on": r[6],
            }
            for r in rows
        ]
    }