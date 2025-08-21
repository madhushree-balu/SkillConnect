from pydantic import BaseModel
from typing import List, Literal

# User Type Enum
UserType = Literal["FREELANCER", "RECRUITER"]


# --------------------------
# Core User & Session Models
# --------------------------

class User(BaseModel):
    userId: int = -1
    username: str
    email: str
    password: str
    userType: UserType


class Session(BaseModel):
    sessionId: str
    userId: int


# --------------------------
# Freelancer Models
# --------------------------

class FreelancerProfile(BaseModel):
    userId: int
    firstName: str
    lastName: str
    education: List["Education"]
    experience: List["Experience"]
    skills: List["Skill"]  # linked via UserSkill


class Education(BaseModel):
    school: str
    degree: str
    fieldOfStudy: str
    startDate: str
    endDate: str
    cgpa: float


class Experience(BaseModel):
    company: str
    position: str
    startDate: str
    endDate: str
    description: str


# --------------------------
# Skills Models
# --------------------------

class Skill(BaseModel):
    skillId: int
    skill: str


class UserSkill(BaseModel):
    userId: int
    skillId: int
