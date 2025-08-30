from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from enum import Enum


class Recruiter(BaseModel):
    recruiterId: int = Field(default=-1, description="Auto-generated recruiter ID")
    name: str = Field(..., min_length=1, description="Recruiter name")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=1, description="Hashed password")
    company: str = ""
    location: str = ""
    website: str = ""
    contact_email: str = ""
    contact_number: str = ""


class JobPost(BaseModel):
    jobId: int = Field(default=-1, description="Auto-generated job ID")
    recruiterId: int = Field(default=-1, description="Associated recruiter ID")
    title: str = Field(..., min_length=1, description="Job title")
    description: str = Field(..., min_length=1, description="Job description")
    location: str = ""
    salary: float = 0.0
    experience: int = 0

class JobSkills(BaseModel):
    jobId: int = Field(..., description="Job ID")
    skillId: int = Field(..., description="Skill ID")

class JobApplications(BaseModel):
    jobId: int = Field(..., description="Job ID")
    freelancerId: int = Field(..., description="Freelancer ID")
    applicationDate: str = ""
    resumeId: int = -1


class Resume(BaseModel):
    resumeId: int = Field(default=-1, description="Auto-generated resume ID")
    freelancerId: int = Field(default=-1, description="Associated freelancer ID")
    name: str = Field(..., min_length=1, description="Resume name")
    pdfData: bytes = Field(..., description="PDF data")


class RecruiterSession(BaseModel):
    sessionId: str = Field(..., description="Unique session identifier")
    recruiterId: int = Field(..., description="Associated recruiter ID")


# --------------------------
# Core User & Session Models
# --------------------------
class User(BaseModel):
    userId: int = Field(default=-1, description="Auto-generated user ID")
    username: str = Field(..., min_length=1, description="Unique username")
    email: str = Field(..., description="Unique email address")
    password: str = Field(..., min_length=1, description="Hashed password")

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
    school: str = ""
    degree: str = ""
    fieldOfStudy: str = ""
    startDate: str = ""
    endDate: Optional[str] = ""
    cgpa: Optional[float] = 0.0


class Experience(BaseModel):
    experienceId: int = Field(default=-1, description="Auto-generated experience ID")
    userId: int = Field(default=-1, description="Associated user ID")
    company: str = ""
    position: str = ""
    startDate: str = ""
    endDate: Optional[str] = ""
    description: Optional[str] = ""


# --------------------------
# Request/Response Models for API
# --------------------------

class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=1)
    email: str
    password: str = Field(..., min_length=8)


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