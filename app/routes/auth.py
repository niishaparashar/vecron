from fastapi import APIRouter, HTTPException, Depends
from starlette.requests import Request
from fastapi.responses import HTMLResponse
from passlib.context import CryptContext
import sqlite3
import re
import os
import json
from datetime import datetime
from app.database import get_db
from app.schemas import RegisterSchema, LoginSchema, ProfileSchema
from authlib.integrations.starlette_client import OAuth

router= APIRouter(prefix="/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID', 'dummy-google-client-id'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET', 'dummy-google-client-secret'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    api_base_url='https://openidconnect.googleapis.com/v1/',
    client_kwargs={'scope': 'openid email profile'}
)


def _oauth_configured(provider: str) -> bool:
    if provider == "google":
        client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
        return bool(client_id and client_secret and not client_id.startswith("dummy-") and not client_secret.startswith("dummy-"))
    return False


def _local_oauth_redirect_uri(provider: str) -> str:
    port = os.getenv("PORT", "8006").strip() or "8006"
    return f"http://localhost:{port}/auth/callback/{provider}"

EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _validate_email(email: str):
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    if not EMAIL_REGEX.match(email):
        raise HTTPException(status_code=400, detail="Invalid email format")


def _validate_non_empty(value: str, message: str):
    if not value:
        raise HTTPException(status_code=400, detail=message)

def hash_password(password:str) -> str:
    return pwd_context.hash(password[:72])

def verify_password(password:str, hashed:str)-> bool:
    return pwd_context.verify(password[:72], hashed)

#-------------REGISTER-----------------------
@router.post("/register")
def register(user: RegisterSchema):
    email = user.email.strip()
    full_name = user.full_name.strip()
    password = user.password

    _validate_non_empty(full_name, "Full name is required")
    _validate_email(email)
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users WHERE email=?", (email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(password)

    cursor.execute("""
        INSERT INTO users (full_name, email, password_hash, joined_on)
        VALUES (?,?,?,?)
    """, (
        full_name,
        email,
        hashed_pw,
        datetime.now().isoformat()
    ))

    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    from app.core.security import create_access_token
    access_token = create_access_token(
        data={"sub": str(user_id)}
    )

    return {
        "message": "Registered",
        "user_id": user_id,
        "access_token": access_token,
        "is_admin": False,
        "profile_completed": 0,
    }

#------------------LOGIN------------------------
@router.post("/login")
def login(user: LoginSchema):
    email = user.email.strip()
    password = user.password

    _validate_email(email)
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, password_hash, full_name, email, is_admin, profile_completed
        FROM users
        WHERE email=?
    """, (email,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id, password_hash, full_name, email, is_admin, profile_completed = row

    if not verify_password(password, password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    from app.core.security import create_access_token

    access_token = create_access_token(
        data={"sub": str(user_id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user_id,
        "full_name": full_name,
        "email": email,
        "is_admin": bool(is_admin),
        "profile_completed": bool(profile_completed),
    }


#-----------------COMPLETE PROFILE-----------------------
@router.post("/complete-profile")
def complete_profile(data: ProfileSchema):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET experience_level=?, preferred_category=?, skills=?, preferred_location=?, preferred_workplace=?,
        profile_completed =1
        WHERE user_id=?
    """, (
        data.experience_level,
        data.preferred_category,
        data.skills,
        data.preferred_location,
        data.preferred_workplace,
        data.user_id
    )
    )
    conn.commit()
    conn.close()

    return {"message": "profile updated"}

@router.put("/update-profile")
def update_profile(payload: dict):
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=400, detail="User ID required")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET
            experience_level = ?,
            preferred_category = ?,
            skills = ?,
            preferred_location = ?,
            preferred_workplace = ?,
            preferred_employment_type = ?
        WHERE user_id = ?
    """, (
        payload.get("experience_level"),
        payload.get("preferred_category"),
        payload.get("skills"),
        payload.get("preferred_location"),
        payload.get("preferred_workplace"),
        payload.get("preferred_employment_type"),
        user_id
    ))

    conn.commit()
    conn.close()

    return {"message": "Profile updated successfully"}

#----------view ur profile------------
@router.get("/me/{user_id}")
def get_my_profile(user_id: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            full_name,
            email,
            experience_level,
            skills,
            preferred_category,
            preferred_workplace,
            preferred_employment_type,
            preferred_location
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    return dict(row)

@router.post("/reset-admin")
def reset_admin(secret: str, new_password: str):

    # Change this secret to something random
    if secret != "VECRON_RESET_2026":
        raise HTTPException(status_code=403, detail="Forbidden")

    conn = get_db()
    cursor = conn.cursor()

    hashed = hash_password(new_password)

    cursor.execute("""
        UPDATE users
        SET password_hash = ?
        WHERE email = ?
    """, (hashed, "vecr0n.adm1n@gmail.com"))

    conn.commit()
    conn.close()

    return {"message": "Admin password reset"}


#------------------OAUTH HELPERS & ROUTERS------------------------

def handle_oauth_user(email: str, full_name: str):
    email = email.lower().strip()
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, full_name, is_admin, profile_completed FROM users WHERE email=?", (email,))
    row = cursor.fetchone()

    profile_completed = 0
    is_admin = 0

    if row:
        user_id, existing_name, is_admin, profile_completed = row
        # If OAuth provides a name but we don't have it, update it
        if not existing_name and full_name:
            cursor.execute("UPDATE users SET full_name=? WHERE user_id=?", (full_name, user_id))
            conn.commit()
    else:
        # Create a new user with placeholder password hash
        hashed_pw = hash_password("OAUTH_USER_PLACEHOLDER_PASS")
        cursor.execute("""
            INSERT INTO users (full_name, email, password_hash, is_admin, profile_completed, joined_on)
            VALUES (?, ?, ?, 0, 0, ?)
        """, (full_name, email, hashed_pw, datetime.now().isoformat()))
        conn.commit()
        user_id = cursor.lastrowid

    conn.close()

    from app.core.security import create_access_token
    access_token = create_access_token(data={"sub": str(user_id)})

    payload = {
        "access_token": access_token,
        "user_id": user_id,
        "full_name": full_name,
        "user_email": email,
        "is_admin": "true" if is_admin else "false",
        "profile_completed": str(profile_completed),
    }

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OAuth Success</title>
    </head>
    <body>
        <p>Signing you in, please wait...</p>
        <script>
            const oauthPayload = {json.dumps(payload)};
            Object.entries(oauthPayload).forEach(([key, value]) => {{
                localStorage.setItem(key, String(value));
            }});
            window.location.href = Number(oauthPayload.profile_completed) === 1 ? "/dashboard.html" : "/profile.html";
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@router.get("/login/google")
async def google_login(request: Request):
    if not _oauth_configured("google"):
        raise HTTPException(
            status_code=503,
            detail="Google OAuth is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET, then restart the server.",
        )
    redirect_uri = _local_oauth_redirect_uri("google")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback/google", name="google_callback")
async def google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        try:
            user_info = await oauth.google.parse_id_token(request, token)
        except Exception:
            response = await oauth.google.get("userinfo", token=token)
            user_info = response.json()
        if not user_info:
            raise HTTPException(status_code=400, detail="Google authentication failed")
        email = user_info.get('email')
        full_name = user_info.get('name') or user_info.get('given_name') or "Google User"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {str(e)}")

    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Google")

    return handle_oauth_user(email, full_name)
