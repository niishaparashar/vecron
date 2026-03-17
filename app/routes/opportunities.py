from fastapi import APIRouter, HTTPException
from app.database import get_db
from urllib.parse import quote_plus, urlparse

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


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


def _resolve_career_url(company_name: str, career_url: str, apply_url: str) -> str:
    # Prefer explicit career URL from source if valid.
    explicit = _domain_root_from_url(career_url) if career_url else ""
    if explicit:
        return career_url

    # Then use company domain from apply URL.
    domain_root = _domain_root_from_url(apply_url)
    if domain_root:
        return f"{domain_root}/careers"

    # Final fallback: searchable careers query.
    return _career_search_url(company_name)


def _fallback_job_description(item: dict) -> str:
    skills = [s.strip() for s in (item.get("skills_required", "") or "").split(",") if s.strip()]
    skills_text = ", ".join(skills[:6]) if skills else "relevant technical and communication skills"
    return (
        f"{item.get('company_name', 'This company')} is hiring for {item.get('title', 'this role')} "
        f"({item.get('employment_type', 'Full-time')}, {item.get('experience_level', 'Any')}) in "
        f"{item.get('location', 'a flexible location')}. "
        f"Key capabilities include {skills_text}."
    )


def _has_column(cursor, col_name: str) -> bool:
    cursor.execute("PRAGMA table_info(opportunities)")
    return any(row[1] == col_name for row in cursor.fetchall())

@router.get("/all")
def get_all_opportunities():
    conn = get_db()
    cursor = conn.cursor()

    has_career = _has_column(cursor, "career_page_url")
    has_apply = _has_column(cursor, "apply_url")
    has_description = _has_column(cursor, "job_description")

    career_sql = "career_page_url" if has_career else "'' AS career_page_url"
    apply_sql = "apply_url" if has_apply else "'' AS apply_url"
    description_sql = "job_description" if has_description else "'' AS job_description"
    
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
            posted_on,
            {career_sql},
            {apply_sql},
            {description_sql}
        FROM opportunities 
        ORDER BY posted_on DESC
    """.format(
        career_sql=career_sql,
        apply_sql=apply_sql,
        description_sql=description_sql,
    ))
    
    rows = cursor.fetchall()
    conn.close()

    # Convert SQLite Row objects to dicts
    opportunities = []
    for row in rows:
        item = dict(row)
        item["career_page_url"] = _resolve_career_url(
            item.get("company_name", ""),
            item.get("career_page_url", ""),
            item.get("apply_url", ""),
        )
        if not (item.get("job_description", "") or "").strip():
            item["job_description"] = _fallback_job_description(item)

        opportunities.append(item)
    
    return {"opportunities": opportunities}


@router.get("/{opportunity_id}")
def get_opportunity(opportunity_id: int):
    conn = get_db()
    cursor = conn.cursor()

    has_career = _has_column(cursor, "career_page_url")
    has_apply = _has_column(cursor, "apply_url")
    has_description = _has_column(cursor, "job_description")

    career_sql = "career_page_url" if has_career else "'' AS career_page_url"
    apply_sql = "apply_url" if has_apply else "'' AS apply_url"
    description_sql = "job_description" if has_description else "'' AS job_description"

    cursor.execute("""
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
            {career_sql},
            {apply_sql},
            {description_sql}
        FROM opportunities
        WHERE opportunity_id = ?
        LIMIT 1
    """.format(
        career_sql=career_sql,
        apply_sql=apply_sql,
        description_sql=description_sql,
    ), (opportunity_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    item = dict(row)
    item["career_page_url"] = _resolve_career_url(
        item.get("company_name", ""),
        item.get("career_page_url", ""),
        item.get("apply_url", ""),
    )
    if not (item.get("job_description", "") or "").strip():
        item["job_description"] = _fallback_job_description(item)

    return item
