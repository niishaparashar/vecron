"""
Replicates the n8n 'VECRON - Opportunity Sync (24h)' workflow:
Fetch Jobs -> Normalize Jobs -> Push to VECRON
Runs on a schedule via GitHub Actions instead of n8n.
"""
import os
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

REMOTIVE_URL = "https://remotive.com/api/remote-jobs?limit=100"
VECRON_URL = "https://vecron.onrender.com/admin/opportunities/ingest"
INGESTION_KEY = os.environ["VECRON_INGESTION_KEY"]  # set as a GitHub Actions secret
PUSH_TIMEOUT_SECONDS = 120
MAX_PUSH_ATTEMPTS = 3


def as_text(value, fallback="Unknown"):
    text = (str(value) if value is not None else "").strip()
    return text or fallback


def map_employment_type(value):
    source = as_text(value, "").lower()
    if "intern" in source:
        return "Internship"
    if "part" in source:
        return "Part-time"
    return "Full-time"


def map_experience(text):
    source = as_text(text, "").lower()
    if any(k in source for k in ("senior", "lead", "5+", "6+")):
        return "Mid"
    if any(k in source for k in ("junior", "1+", "2+")):
        return "Junior"
    if any(k in source for k in ("intern", "entry", "fresher")):
        return "Fresher"
    return "Junior"


def map_department(title):
    source = as_text(title, "").lower()
    if any(k in source for k in ("data", "ml", "ai")):
        return "Data"
    if any(k in source for k in ("devops", "site reliability", "sre")):
        return "Operations"
    if any(k in source for k in ("analyst", "product")):
        return "Product"
    return "Engineering"


def map_category(title, department):
    source = as_text(title, "").lower()
    if department == "Data":
        return "Analytics & AI"
    if department == "Operations":
        return "Infrastructure"
    if "analyst" in source or "product" in source:
        return "Business & Strategy"
    return "Software Engineering"


def map_workplace_type(candidate):
    source = as_text(candidate, "").lower()
    if "hybrid" in source:
        return "Hybrid"
    if "remote" in source:
        return "Remote"
    return "On-site"


def extract_skills(job):
    for key in ("tags", "skills", "keywords"):
        candidate = job.get(key)
        if isinstance(candidate, list) and candidate:
            return ", ".join(as_text(x, "") for x in candidate if as_text(x, ""))
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return "Communication, Problem Solving"


def to_iso_date(value):
    if not value:
        return datetime.now(timezone.utc).date().isoformat()
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value[:19], fmt).date().isoformat()
        except (ValueError, TypeError):
            continue
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except Exception:
        return datetime.now(timezone.utc).date().isoformat()


def career_page_url_from_apply_url(apply_url):
    if not apply_url:
        return ""
    try:
        parsed = urlparse(apply_url)
        if not parsed.scheme or not parsed.netloc:
            return ""
        return f"{parsed.scheme}://{parsed.netloc}/careers"
    except Exception:
        return ""


def normalize(raw_jobs):
    opportunities = []
    for job in raw_jobs:
        title = as_text(job.get("title"), "Software Engineer")
        company = as_text(
            job.get("company_name") or job.get("company") or job.get("companyName"),
            "Unknown Company",
        )
        employment_type = map_employment_type(
            job.get("job_type") or job.get("employment_type") or job.get("type")
        )
        experience_level = map_experience(job.get("candidate_required_location") or title)
        department = map_department(title)
        category = map_category(title, department)
        location = as_text(job.get("candidate_required_location") or job.get("location"), "Remote")
        workplace_type = map_workplace_type(location)
        description = as_text(
            job.get("description") or job.get("job_description") or job.get("body") or "",
            "No detailed description provided.",
        )
        apply_url = as_text(job.get("url") or job.get("apply_url") or job.get("apply_link") or "", "")

        opp = {
            "company_name": company,
            "title": title,
            "employment_type": employment_type,
            "experience_level": experience_level,
            "skills_required": extract_skills(job),
            "department": department,
            "category": category,
            "location": location,
            "workplace_type": workplace_type,
            "posted_on": to_iso_date(
                job.get("publication_date") or job.get("posted_on") or job.get("created_at")
            ),
            "career_page_url": career_page_url_from_apply_url(apply_url),
            "apply_url": apply_url,
            "job_description": description,
        }
        opportunities.append(opp)

    return [o for o in opportunities if o["company_name"] and o["title"] and o["location"] and o["posted_on"]]


def main():
    resp = requests.get(REMOTIVE_URL, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    raw_jobs = data.get("jobs") or data.get("results") or []

    opportunities = normalize(raw_jobs)
    print(f"Fetched {len(raw_jobs)} jobs, normalized {len(opportunities)}")

    push_resp = None
    for attempt in range(1, MAX_PUSH_ATTEMPTS + 1):
        try:
            push_resp = requests.post(
                VECRON_URL,
                json={"opportunities": opportunities},
                headers={
                    "X-Ingestion-Key": INGESTION_KEY,
                    "Content-Type": "application/json",
                },
                timeout=PUSH_TIMEOUT_SECONDS,
            )
            break
        except requests.exceptions.Timeout:
            if attempt == MAX_PUSH_ATTEMPTS:
                raise
            wait_seconds = attempt * 5
            print(f"Push attempt {attempt} timed out after {PUSH_TIMEOUT_SECONDS}s. Retrying in {wait_seconds}s...")
            time.sleep(wait_seconds)

    print(f"Push status: {push_resp.status_code}")
    print(push_resp.text[:1000])

    if push_resp.status_code >= 400:
        sys.exit(1)


if __name__ == "__main__":
    main()