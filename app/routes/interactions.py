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

    if payload.interaction_type == "save":
        cursor.execute(
            """
            SELECT interaction_id
            FROM interactions
            WHERE user_id = ? AND opportunity_id = ? AND interaction_type = 'save'
            LIMIT 1
            """,
            (user_id, payload.opportunity_id),
        )
        already_saved = cursor.fetchone() is not None
        if already_saved:
            conn.close()
            return {"status": "already saved", "saved": True}

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

    return {"status": "interaction logged", "saved": payload.interaction_type == "save"}


@router.get("/saved")
def get_saved_jobs(user_id: int = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            o.opportunity_id,
            o.company_name,
            o.title,
            o.experience_level,
            o.skills_required,
            o.location,
            o.workplace_type,
            o.apply_url,
            o.career_page_url,
            o.job_description,
            MAX(i.interacted_at) AS saved_at
        FROM interactions i
        JOIN opportunities o ON o.opportunity_id = i.opportunity_id
        WHERE i.user_id = ? AND i.interaction_type = 'save'
        GROUP BY
            o.opportunity_id, o.company_name, o.title, o.experience_level,
            o.skills_required, o.location, o.workplace_type, o.apply_url,
            o.career_page_url, o.job_description
        ORDER BY saved_at DESC
        """,
        (user_id,),
    )
    saved_jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"saved_jobs": saved_jobs}
