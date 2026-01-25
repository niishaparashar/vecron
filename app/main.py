from fastapi import FastAPI
from app.routes.auth import router as auth_router
from app.routes.recommendations import router as recommend_router
from app.routes.interactions import router as interaction_router
from app.routes.admin import router as admin_router
from app.routes.opportunities import router as opportunities_router






from fastapi.staticfiles import StaticFiles
import os
app = FastAPI()

app.include_router(auth_router)
app.include_router(recommend_router)
app.include_router(interaction_router)
app.include_router(admin_router)
app.include_router(opportunities_router)
'''@app.get("/")
def root():
    return {"status": "VECRON backend running"}'''

# Serve frontend files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "js")), name="js")  # optional for /static/js
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

