import csv
import os
from urllib.parse import quote_plus, urlparse
from fastapi import APIRouter, Header, HTTPException, Depends
from app.database import get_db
from app.core.deps import get_current_admin
from datetime import date
from app.schemas import OpportunityBatchInSchema


router = APIRouter(prefix="/admin", tags=["Admin"])
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.getenv("OPPORTUNITY_CSV_PATH", os.path.join(BASE_DIR, "db", "opportunity.csv"))
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
    "career_page_url",
    "apply_url",
    "job_description",
]


def _ensure_opportunity_columns(conn):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = current_schema() AND table_name = ?
        """,
        ("opportunities",),
    )
    existing = {row["column_name"] for row in cursor.fetchall()}

    required_columns = {
        "career_page_url": "TEXT DEFAULT ''",
        "apply_url": "TEXT DEFAULT ''",
        "job_description": "TEXT DEFAULT ''",
    }

    for col_name, col_type in required_columns.items():
        if col_name not in existing:
            cursor.execute(f"ALTER TABLE opportunities ADD COLUMN {col_name} {col_type}")

    conn.commit()


def _ensure_ingestion_log_table(conn):
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ingestion_logs(
            ingestion_log_id SERIAL PRIMARY KEY,
            status TEXT NOT NULL,
            received_count INTEGER NOT NULL DEFAULT 0,
            inserted_count INTEGER NOT NULL DEFAULT 0,
            updated_count INTEGER NOT NULL DEFAULT 0,
            error_message TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


def _record_ingestion_log(
    conn,
    status: str,
    received_count: int = 0,
    inserted_count: int = 0,
    updated_count: int = 0,
    error_message: str = "",
):
    _ensure_ingestion_log_table(conn)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO ingestion_logs (
            status,
            received_count,
            inserted_count,
            updated_count,
            error_message
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            status,
            received_count,
            inserted_count,
            updated_count,
            (error_message or "")[:500],
        ),
    )
    conn.commit()


def _record_ingestion_failure_without_blocking(received_count: int, error_message: str):
    conn = None
    try:
        conn = get_db()
        _record_ingestion_log(
            conn,
            status="failed",
            received_count=received_count,
            error_message=error_message,
        )
    except Exception:
        pass
    finally:
        if conn:
            conn.close()


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
            posted_on,
            career_page_url,
            apply_url,
            job_description
        FROM opportunities
        ORDER BY opportunity_id
        """
    )
    rows = cursor.fetchall()

    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(CSV_HEADERS)
        for row in rows:
            writer.writerow([row[key] for key in CSV_HEADERS])


def _domain_root_from_url(url: str) -> str:
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return ""
        return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        return ""


def _career_search_url(company_name: str) -> str:
    company = (company_name or "").strip()
    if not company:
        return ""
    query = quote_plus(f"{company} careers")
    return f"https://www.google.com/search?q={query}"


def _resolve_career_url(company_name: str, career_page_url: str, apply_url: str) -> str:
    explicit = _domain_root_from_url(career_page_url) if career_page_url else ""
    if explicit:
        return career_page_url

    domain_root = _domain_root_from_url(apply_url)
    if domain_root:
        return f"{domain_root}/careers"

    return _career_search_url(company_name)


def _fallback_job_description(
    company_name: str,
    title: str,
    skills_required: str,
    location: str,
    employment_type: str,
    experience_level: str,
) -> str:
    skills = [s.strip() for s in (skills_required or "").split(",") if s.strip()]
    skills_text = ", ".join(skills[:6]) if skills else "relevant technical and communication skills"
    return (
        f"{company_name} is hiring a {title} role ({employment_type}, {experience_level}) "
        f"based in {location}. The role focuses on delivering project outcomes, collaborating with teams, "
        f"and applying skills such as {skills_text}."
    )

@router.get("/analytics")
def get_admin_insights(admin_id: int = Depends(get_current_admin)):
    conn = get_db()
    cursor = conn.cursor()

    # Total users
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    # Users registered today
    cursor.execute("""
        SELECT COUNT(*) 
        FROM users 
        WHERE joined_on >= CURRENT_DATE
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
def recent_users(limit: int | None=None, admin_id: int = Depends(get_current_admin)):
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


@router.get("/ingestion-logs")
def get_ingestion_logs(limit: int = 10, admin_id: int = Depends(get_current_admin)):
    limit = min(max(limit, 1), 50)
    conn = get_db()
    _ensure_ingestion_log_table(conn)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            ingestion_log_id,
            status,
            received_count,
            inserted_count,
            updated_count,
            error_message,
            created_at
        FROM ingestion_logs
        ORDER BY created_at DESC, ingestion_log_id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()

    logs = [dict(row) for row in rows]
    return {
        "latest": logs[0] if logs else None,
        "logs": logs,
    }


@router.post("/opportunities/ingest")
def ingest_opportunities(
    payload: OpportunityBatchInSchema,
    x_ingestion_key: str | None = Header(default=None, alias="X-Ingestion-Key"),
):
    expected_key = os.getenv("N8N_INGESTION_KEY")
    if not expected_key:
        _record_ingestion_failure_without_blocking(
            len(payload.opportunities),
            "N8N_INGESTION_KEY is not configured on the backend",
        )
        raise HTTPException(
            status_code=500,
            detail="N8N_INGESTION_KEY is not configured on the backend",
        )
    if x_ingestion_key != expected_key:
        _record_ingestion_failure_without_blocking(
            len(payload.opportunities),
            "Invalid ingestion key",
        )
        raise HTTPException(status_code=401, detail="Invalid ingestion key")

    conn = get_db()
    _ensure_opportunity_columns(conn)
    _ensure_ingestion_log_table(conn)
    cursor = conn.cursor()

    inserted = 0
    updated = 0

    try:
        for job in payload.opportunities:
            career_page_url = (job.career_page_url or "").strip()
            apply_url = (job.apply_url or "").strip()
            job_description = (job.job_description or "").strip()
            career_page_url = _resolve_career_url(
                job.company_name,
                career_page_url,
                apply_url,
            )
            if not job_description:
                job_description = _fallback_job_description(
                    job.company_name,
                    job.title,
                    job.skills_required,
                    job.location,
                    job.employment_type,
                    job.experience_level,
                )

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
                        workplace_type = ?,
                        career_page_url = ?,
                        apply_url = ?,
                        job_description = ?
                    WHERE opportunity_id = ?
                    """,
                    (
                        job.employment_type,
                        job.experience_level,
                        job.skills_required,
                        job.department,
                        job.category,
                        job.workplace_type,
                        career_page_url,
                        apply_url,
                        job_description,
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
                        posted_on,
                        career_page_url,
                        apply_url,
                        job_description
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                        career_page_url,
                        apply_url,
                        job_description,
                    ),
                )
                inserted += 1

        conn.commit()
        _sync_opportunity_csv(conn)
        _record_ingestion_log(
            conn,
            status="success",
            received_count=len(payload.opportunities),
            inserted_count=inserted,
            updated_count=updated,
        )
    except Exception as exc:
        conn.rollback()
        _record_ingestion_log(
            conn,
            status="failed",
            received_count=len(payload.opportunities),
            inserted_count=inserted,
            updated_count=updated,
            error_message=str(exc),
        )
        conn.close()
        raise HTTPException(status_code=500, detail="Opportunity ingestion failed")

    conn.close()

    return {
        "received": len(payload.opportunities),
        "inserted": inserted,
        "updated": updated,
        "csv_path": CSV_PATH,
    }
