from pydantic import BaseModel, Field
from typing import List

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


class OpportunityInSchema(BaseModel):
    company_name: str = Field(min_length=1)
    title: str = Field(min_length=1)
    employment_type: str = Field(min_length=1)
    experience_level: str = Field(min_length=1)
    skills_required: str = Field(min_length=1)
    department: str = Field(min_length=1)
    category: str = Field(min_length=1)
    location: str = Field(min_length=1)
    workplace_type: str = Field(min_length=1)
    posted_on: str = Field(min_length=10, max_length=10)


class OpportunityBatchInSchema(BaseModel):
    opportunities: List[OpportunityInSchema]

