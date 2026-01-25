from pydantic import BaseModel

class RegisterSchema(BaseModel):
    full_name:str
    email:str
    password:str

class LoginSchema(BaseModel):
    email:str
    password: str

class ProfileSchema(BaseModel):
    user_id:int
    experience_level:str
    preferred_category: str
    skills: str
    preferred_location :str
    preferred_workplace: str

