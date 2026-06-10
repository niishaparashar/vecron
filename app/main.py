from fastapi import FastAPI, Request
from app.routes.auth import router as auth_router
from app.routes.recommendations import router as recommend_router
from app.routes.interactions import router as interaction_router
from app.routes.admin import router as admin_router
from app.routes.opportunities import router as opportunities_router

from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import os
from db.create_tables import create_tables

app = FastAPI()
create_tables()

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "VECRON_SUPER_SECRET_SESSION_KEY_2026")
)
@app.get("/debug-env")
def debug_env():
    return {
        "APP_BASE_URL": os.getenv("APP_BASE_URL"),
        "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", "")[:10] + "...",
        "SESSION_SECRET": os.getenv("SESSION_SECRET", "")[:5] + "...",
    }
@app.middleware("http")
async def canonical_localhost_redirect(request: Request, call_next):
    host = request.url.hostname or ""
    if host in {"127.0.0.1", "::1"}:
        port = request.url.port or int(os.getenv("PORT", "8006"))
        target = request.url.replace(netloc=f"localhost:{port}")
        return RedirectResponse(url=str(target), status_code=307)
    return await call_next(request)

app.include_router(auth_router)
app.include_router(recommend_router)
app.include_router(interaction_router)
app.include_router(admin_router)
app.include_router(opportunities_router)

# Serve frontend files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "js")), name="js")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")