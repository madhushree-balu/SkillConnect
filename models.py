import pydantic
import typing

"""
-- Recruiters Table
CREATE TABLE IF NOT EXISTS recruiters (
    id INTEGER PRIMARY KEY AUTO INCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Company Table
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTO INCREMENT,
    username TEXT UNIQUE NOT NULL,
    companyName TEXT NOT NULL,
    companyPhone TEXT NOT NULL,
    companyAddress TEXT NOT NULL,
    companyDescription TEXT NOT NULL,
    employeeSize INTEGER NOT NULL DEFAULT 1
);

-- RecruiterCompanies Table
CREATE TABLE IF NOT EXISTS recruiterCompanies (
    recruiterId INTEGER NOT NULL,
    companyId INTEGER NOT NULL,
    role TEXT NOT NULL DEFAULT "RECRUITER" CHECK role IN ('RECRUITER', 'ADMIN'),
    PRIMARY KEY (recruiterId, companyId),
    FOREIGN KEY (recruiterId) REFERENCES recruiters(id) ON CASCADE DELETE,
    FOREIGN KEY (companyId) REFERENCES companies(id) ON CASCADE DELETE
);

-- Job Posts
CREATE TABLE IF NOT EXISTS jobPosts (
    id INTEGER PRIMARY KEY AUTO INCREMENT,
    jobTitle TEXT,
    jobDescription TEXT,
    experienceRequired INTEGER,
    jobType TEXT CHECK jobType IN ('FULL-TIME', 'PART-TIME', 'INTERN', 'TRAINING')
);

-- Skills Table
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTO INCREMENT,
    skill TEXT UNIQUE NOT NULL
);

-- jobPost to Skills
CREATE TABLE IF NOT EXISTS postSkills (
    postId INTEGER NOT NULL,
    skillId INTEGER NOT NULL,
    PRIMARY KEY (postId, skillId),
    FOREIGN KEY postId REFERENCES post(id) ON CASCADE DELETE,
    FOREIGN KEY skillId REFERENCES skills(id) ON CASCADE DELETE
)

-- Recruiter Company Posts
CREATE TABLE IF NOT EXISTS recruiterCompanyPosts (
    recruiterId INTEGER NOT NULL,
    companyId INTEGER NOT NULL,
    postId INTEGER NOT NULL,
    PRIMARY KEY (recruiterId, companyId, postId),
    FOREIGN KEY (recruiterId) REFERENCES recruiters(id) ON CASCADE DELETE,
    FOREIGN KEY (companyId) REFERENCES companies(id) ON CASCADE DELETE,
    FOREIGN KEY (postId) REFERENCES jonPosts(id) ON CASCADE DELETE
)


-- Freelancers Table
CREATE TABLE IF NOT EXISTS freelancers (
    id INTEGER PRIMARY KEY AUTO INCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Freelancer Details
CREATE TABLE IF NOT EXISTS freelancerDetails (
    freelancerId INTEGER UNIQUE NOT NULL,
    firstName VARCHAR(255),
    middleName VARCHAR(255),
    lastName VARCHAR(255),
    phoneNumber VARCHAR(20),
    contactEmail VARCHAR(255),
    about TEXT,
    dateOfBirth DATE,
)

-- Freelancer Educations
CREATE TABLE IF NOT EXISTS educations (
    id INTEGER PRIMARY KEY AUTO INCREMENT,
    freelancerId INTEGER NOT NULL,
    course TEXT,
    degree TEXT,
    school TEXT,
    startDate DATE,
    endDate DATE CHECK (startDate <= endDate),
    cgpa DOUBLE,
    FOREIGN KEY freelancerId REFERENCES freelancers(id) ON CASCADE DELETE
);

-- Freelancer Experiences
CREATE TABLE IF NOT EXISTS experiences (
    id INTEGER PRIMARY KEY AUTO INCREMENT,
    freelancerId INTEGER NOT NULL,
    companyName TEXT,
    startDate DATE,
    endDate DATE CHECK (startDate <= endDate),
    role VARCHAR(255),
    FOREIGN KEY freelancerId REFERENCES freelancers(id) ON CASCADE DELETE
);

-- Freelancers to Skills
CREATE TABLE IF NOT EXISTS freelancerSkills (
    freelancerId INTEGER NOT NULL,
    skillId INTEGER NOT NULL,
    PRIMARY KEY (freelancerId, skillId),
    FOREIGN KEY freelancerId REFERENCES freelancers(id) ON CASCADE DELETE,
    FOREIGN KEY skillId REFERENCES skills(id) ON CASCADE DELETE
);

-- Applications Table
CREATE TABLE IF NOT EXISTS applications (
    postId INTEGER NOT NULL,
    freelancerId INTEGER NOT NULL,
    status TEXT CHECK status IN ('APPLIED', 'SEEN', 'ACCEPTED', 'REJECTED'),
    appliedOn DATE,
    PRIMARY KEY (postId, freelancerId),
    FOREIGN KEY (postId) REFERENCES jobPosts(id) ON CASCADE DELETE,
    FOREIGN KEY (freelancerId) REFERENCES freelancers(id) ON CASCADE DELETE
);
"""

class Recruiter(pydantic.BaseModel):
    id: int
    username: str
    email: str
    password: str

class Company(pydantic.BaseModel):
    id: int
    username: str
    companyName: str
    companyPhone: str
    companyAddress: str
    companyDescription: str
    employeeSize: int
    
class JobPost(pydantic.BaseModel):
    id: int
    title: str
    description: str
    experience: int
    jobType: str
    location: str
    salary: float

class Skill(pydantic.BaseModel):
    id: int
    skill: str

class PostSkill(pydantic.BaseModel):
    postId: int
    skillId: int


class RecruiterCompany(pydantic.BaseModel):
    recruiterId: int
    companyId: int
    role: str = "RECRUITER"

class RecruiterCompanyPost(pydantic.BaseModel):
    recruiterId: int
    companyId: int
    postId: int
    postedOn: str
    validTill: str

class Freelancer(pydantic.BaseModel):
    id: int
    username: str
    email: str
    password: str

class FreelancerDetails(pydantic.BaseModel):
    freelancerId: int
    firstName: str
    middleName: str
    lastName: str
    phoneNumber: str
    contactEmail: str
    about: str
    dateOfBirth: str

class Education(pydantic.BaseModel):
    id: int
    freelancerId: int
    course: str
    degree: str
    school: str
    startDate: str
    endDate: str
    cgpa: float

class Experience(pydantic.BaseModel):
    id: int
    freelancerId: int
    companyName: str
    startDate: str
    endDate: str
    description: str
    role: str

class FreelancerSkill(pydantic.BaseModel):
    freelancerId: int
    skillId: int

class Application(pydantic.BaseModel):
    jobPostId: int
    freelancerId: int
    status: str
    appliedOn: str
    resumeId: int

class Resume(pydantic.BaseModel):
    id: int
    freelancerId: int
    name: str
    pdfData: bytes