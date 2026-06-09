from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_access_token
from app.database import get_db

security = HTTPBearer()

def get_current_user(
        credentials: HTTPAuthorizationCredentials= Depends(security)
):
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return int(payload["sub"])

def get_current_admin(
        user_id: int = Depends(get_current_user)
):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT is_admin FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row or not row["is_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized as admin")
    
    return user_id
