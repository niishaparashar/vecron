from datetime import datetime
from fastapi import APIRouter, Depends
from app.database import get_db
from app.core.deps import get_current_user
from app.schemas import InteractionInSchema

router = APIRouter(prefix="/interactions", tags=["Interactions"])


@router.post("/interact")
def log_interaction(
    payload: InteractionInSchema,
    user_id: int = Depends(get_current_user),
):
    weight_map = {
        "view": 1,
        "save": 3,
        "apply": 5,
    }
    weight = weight_map.get(payload.interaction_type, 1)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO interactions(
            user_id,
            opportunity_id,
            interaction_type,
            interaction_weight,
            interacted_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            payload.opportunity_id,
            payload.interaction_type,
            weight,
            datetime.now().isoformat(),
        ),
    )

    conn.commit()
    conn.close()

    return {"status": "interaction logged"}
