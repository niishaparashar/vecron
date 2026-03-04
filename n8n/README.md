# n8n Opportunity Automation

This folder contains an n8n workflow that runs every 24 hours, fetches job postings, maps them to VECRON fields, and pushes them to the backend ingestion endpoint.

## What it updates

The workflow sends jobs to:

`POST /admin/opportunities/ingest`

The backend then:

- upserts rows into `opportunities` table
- rewrites `db/opportunity.csv` with all required columns:
  - `opportunity_id`
  - `company_name`
  - `title`
  - `employment_type`
  - `experience_level`
  - `skills_required`
  - `department`
  - `category`
  - `location`
  - `workplace_type`
  - `posted_on`

## Backend setup

Set this environment variable before starting FastAPI:

`N8N_INGESTION_KEY=<your-strong-shared-secret>`

## n8n setup

Import:

`n8n/opportunity_ingest_workflow.json`

Set these env vars in n8n:

- `VECRON_API_BASE_URL` (example: `http://localhost:8000`)
- `N8N_INGESTION_KEY` (must match backend)
- `JOBS_SOURCE_URL` (optional override)
  - default in workflow: `https://remotive.com/api/remote-jobs?limit=100`

## Notes

- Dedupe key is: `company_name + title + location + posted_on`.
- Workflow is scheduled every 24 hours.
- If the job source changes fields, update the "Normalize Jobs" code node in n8n.

## 2-minute local smoke test

From `vecron/n8n` in PowerShell:

```powershell
$env:N8N_INGESTION_KEY = "replace-with-your-secret"
.\test_ingest.ps1 -ApiBaseUrl "http://localhost:8000"
```

Optional custom payload:

```powershell
.\test_ingest.ps1 -ApiBaseUrl "http://localhost:8000" -PayloadPath ".\sample_opportunities_payload.json"
```
