from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from enum import Enum

# User Type Enum
class UserType(Enum):
    FREELANCER = "FREELANCER"
    EMPLOYER = "RECRUITER"

# --------------------------
# Core User & Session Models
# --------------------------

class User(BaseModel):
    userId: int = Field(default=-1, description="Auto-generated user ID")
    username: str = Field(..., min_length=1, description="Unique username")
    email: str = Field(..., description="Unique email address")
    password: str = Field(..., min_length=1, description="Hashed password")
    userType: UserType


class UserProfile(BaseModel):
    userId: int = Field(..., description="User ID")
    firstName: str = ""
    middleName: str = ""
    lastName: str = ""
    summary: str = ""
    phoneNumber: str = ""
    address: str = ""
    personalWebsite: str = ""
    contactEmail: str = ""


class Session(BaseModel):
    sessionId: str = Field(..., description="Unique session identifier")
    userId: int = Field(..., description="Associated user ID")


# --------------------------
# Skills Models
# --------------------------

class Skill(BaseModel):
    skillId: int = Field(default=-1, description="Auto-generated skill ID")
    skill: str = Field(..., min_length=1, description="Skill name")


class UserSkill(BaseModel):
    userId: int = Field(..., description="User ID")
    skillId: int = Field(..., description="Skill ID")


# --------------------------
# Profile Related Models
# --------------------------

class Education(BaseModel):
    educationId: int = Field(default=-1, description="Auto-generated education ID")
    userId: int = Field(default=-1, description="Associated user ID")
    school: str = Field(..., min_length=1, description="School/University name")
    degree: str = Field(..., min_length=1, description="Degree obtained")
    fieldOfStudy: str = Field(..., min_length=1, description="Field of study")
    startDate: str = Field(..., description="Start date (YYYY-MM-DD format)")
    endDate: Optional[str] = Field(default=None, description="End date (YYYY-MM-DD format, null if ongoing)")
    cgpa: Optional[float] = Field(default=None, ge=0.0, le=10.0, description="CGPA score")


class Experience(BaseModel):
    experienceId: int = Field(default=-1, description="Auto-generated experience ID")
    userId: int = Field(default=-1, description="Associated user ID")
    company: str = Field(..., min_length=1, description="Company name")
    position: str = Field(..., min_length=1, description="Job position/title")
    startDate: str = Field(..., description="Start date (YYYY-MM-DD format)")
    endDate: Optional[str] = Field(default=None, description="End date (YYYY-MM-DD format, null if current)")
    description: Optional[str] = Field(default=None, description="Job description")


# --------------------------
# Request/Response Models for API
# --------------------------

class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=1)
    email: str
    password: str = Field(..., min_length=8)
    userType: UserType


class LoginRequest(BaseModel):
    email: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    password: str = Field(..., min_length=1)


class UpdateFreelancerProfileRequest(BaseModel):
    firstName: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)


class AddEducationRequest(BaseModel):
    school: str = Field(..., min_length=1)
    degree: str = Field(..., min_length=1)
    fieldOfStudy: str = Field(..., min_length=1)
    startDate: str
    endDate: Optional[str]
    cgpa: Optional[float] = Field(default=None, ge=0.0, le=10.0)


class AddExperienceRequest(BaseModel):
    company: str = Field(..., min_length=1)
    position: str = Field(..., min_length=1)
    startDate: str
    endDate: Optional[str]
    description: Optional[str] = Field(default=None)


class AddSkillRequest(BaseModel):
    skill: str = Field(..., min_length=1)


# --------------------------
# Response Models
# --------------------------

class UserResponse(BaseModel):
    userId: int
    username: str
    email: str
    userType: UserType


class LoginResponse(BaseModel):
    sessionId: str
    user: UserResponse


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[str] = None