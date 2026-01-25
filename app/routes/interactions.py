from fastapi import APIRouter
from app.database import get_db  # ← Use your centralized DB function
from datetime import datetime
from fastapi import Depends  
from app.core.deps import get_current_user

router = APIRouter(prefix="/interactions", tags=["Interactions"])  # ← add prefix & tags for clarity

@router.post("/interact")
def log_interaction(opportunity_id: int, interaction_type: str,):

    weight_map = {
        "view": 1,
        "save": 3,
        "apply": 5
    }
    weight = weight_map.get(interaction_type, 1)
    
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO interactions(
            user_id,
            opportunity_id,
            interaction_type,
            interaction_weight,
            interacted_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, opportunity_id, interaction_type, weight, datetime.now().isoformat()))

    conn.commit()
    conn.close()

    return {"status": "interaction logged"}




