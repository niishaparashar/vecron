from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
import sqlite3
from datetime import datetime
from app.database import get_db
from app.schemas import RegisterSchema, LoginSchema, ProfileSchema

router= APIRouter(prefix="/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password:str) -> str:
    return pwd_context.hash(password[:72])

def verify_password(password:str, hashed:str)-> bool:
    return pwd_context.verify(password[:72], hashed)

#-------------REGISTER-----------------------
@router.post("/register")
def register(user: RegisterSchema):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users WHERE email=?", (user.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)

    cursor.execute("""
        INSERT INTO users (full_name, email, password_hash, joined_on)
        VALUES (?,?,?,?)
    """, (
        user.full_name,
        user.email,
        hashed_pw,
        datetime.now().isoformat()
    ))

    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    return {"message": "Registered", "user_id": user_id}

#------------------LOGIN------------------------
@router.post("/login")
def login(user: LoginSchema):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, password_hash, full_name, email
        FROM users
        WHERE email=?
    """, (user.email,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id, password_hash, full_name, email = row

    if not verify_password(user.password, password_hash):
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
        "email": email
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
