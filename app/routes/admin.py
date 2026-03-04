import csv
import os
from fastapi import APIRouter, Header, HTTPException
from app.database import get_db
from datetime import date
from app.schemas import OpportunityBatchInSchema


router = APIRouter(prefix="/admin", tags=["Admin"])
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(BASE_DIR, "db", "opportunity.csv")
CSV_HEADERS = [
    "opportunity_id",
    "company_name",
    "title",
    "employment_type",
    "experience_level",
    "skills_required",
    "department",
    "category",
    "location",
    "workplace_type",
    "posted_on",
]


def _sync_opportunity_csv(conn):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            opportunity_id,
            company_name,
            title,
            employment_type,
            experience_level,
            skills_required,
            department,
            category,
            location,
            workplace_type,
            posted_on
        FROM opportunities
        ORDER BY opportunity_id
        """
    )
    rows = cursor.fetchall()

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(CSV_HEADERS)
        for row in rows:
            writer.writerow([row[key] for key in CSV_HEADERS])

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


@router.post("/opportunities/ingest")
def ingest_opportunities(
    payload: OpportunityBatchInSchema,
    x_ingestion_key: str | None = Header(default=None, alias="X-Ingestion-Key"),
):
    expected_key = os.getenv("N8N_INGESTION_KEY")
    if not expected_key:
        raise HTTPException(
            status_code=500,
            detail="N8N_INGESTION_KEY is not configured on the backend",
        )
    if x_ingestion_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid ingestion key")

    conn = get_db()
    cursor = conn.cursor()

    inserted = 0
    updated = 0

    for job in payload.opportunities:
        cursor.execute(
            """
            SELECT opportunity_id
            FROM opportunities
            WHERE lower(company_name) = lower(?)
              AND lower(title) = lower(?)
              AND lower(location) = lower(?)
              AND date(posted_on) = date(?)
            LIMIT 1
            """,
            (job.company_name, job.title, job.location, job.posted_on),
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                """
                UPDATE opportunities
                SET
                    employment_type = ?,
                    experience_level = ?,
                    skills_required = ?,
                    department = ?,
                    category = ?,
                    workplace_type = ?
                WHERE opportunity_id = ?
                """,
                (
                    job.employment_type,
                    job.experience_level,
                    job.skills_required,
                    job.department,
                    job.category,
                    job.workplace_type,
                    existing["opportunity_id"],
                ),
            )
            updated += 1
        else:
            cursor.execute(
                """
                INSERT INTO opportunities (
                    company_name,
                    title,
                    employment_type,
                    experience_level,
                    skills_required,
                    department,
                    category,
                    location,
                    workplace_type,
                    posted_on
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.company_name,
                    job.title,
                    job.employment_type,
                    job.experience_level,
                    job.skills_required,
                    job.department,
                    job.category,
                    job.location,
                    job.workplace_type,
                    job.posted_on,
                ),
            )
            inserted += 1

    conn.commit()
    _sync_opportunity_csv(conn)
    conn.close()

    return {
        "received": len(payload.opportunities),
        "inserted": inserted,
        "updated": updated,
        "csv_path": CSV_PATH,
    }
