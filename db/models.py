import pydantic
import typing
import sqlite3
from db.sql_commands import *
from datetime import datetime
from typing import Optional


def execute(query, params):
    conn = None
    try:
        conn = sqlite3.connect("database.db")
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        lastrowid = cursor.lastrowid
        conn.close()
        return lastrowid
    except Exception as e:
        print("\nError in execute query: ", e)
        return None
    finally:
        if conn:
            conn.close()


def fetch(query, params, one=False):
    conn = None
    try:
        conn = sqlite3.connect("database.db")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        if one:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        print("\nError in fetch query: ", e)
        return None
    finally:
        if conn:
            conn.close()


class BaseModel(pydantic.BaseModel):
    @property
    def tableName(self):
        # Use class name directly (PascalCase) to match SQL table names
        return self.__class__.__name__

    def insert(self):
        data = self.model_dump()
        # Remove auto-generated fields
        exclude_fields = {'id', 'createdAt', 'updatedAt'}
        filtered_data = {k: v for k, v in data.items() if k not in exclude_fields}
        return execute(insertQueries[self.tableName], list(filtered_data.values()))
    
    @classmethod
    def get(cls, **kwargs):
        if not kwargs:
            return None

        data = fetch(
            "SELECT * FROM " + cls.__name__ + " WHERE " + " AND ".join([f"{k} = ?" for k in kwargs]),
            list(kwargs.values()),
            one=True
        )
        if not data:
            return None
        
        return cls(**dict(data))

    @classmethod
    def getAll(cls, **kwargs):
        if not kwargs:
            data = fetch("SELECT * FROM " + cls.__name__, ())
        else:
            data = fetch(
                "SELECT * FROM " + cls.__name__ + " WHERE " + " AND ".join([f"{k} = ?" for k in kwargs]),
                list(kwargs.values())
            )
        
        if not data:
            return []
        
        result = []
        for row in data:
            instance = cls(**dict(row))
            result.append(instance)
        return result


class DataModel(BaseModel):
    """For tables with id field"""
    id: int = -1
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    def update(self, **kwargs):
        if not kwargs:
            kwargs = self.model_dump(exclude={"id", "createdAt", "updatedAt"})

        return execute(
            "UPDATE " + self.__class__.__name__ + " SET " + ", ".join([f"{k} = ?" for k in kwargs]) + " WHERE id = ?",
            list(kwargs.values()) + [self.id]
        )
        
    def delete(self):
        return execute(
            "DELETE FROM " + self.__class__.__name__ + " WHERE id = ?",
            (self.id,)
        )


class JunctionModel(BaseModel):
    """For junction tables without id field"""
    createdAt: Optional[str] = None
    
    def delete(self, **kwargs):
        if not kwargs:
            kwargs = self.model_dump(exclude={"createdAt"})

        return execute(
            "DELETE FROM " + self.__class__.__name__ + " WHERE " + " AND ".join([f"{k} = ?" for k in kwargs]),
            list(kwargs.values())
        )

    def update(self, new_values, where_conditions):
        """Update junction table records with specific where conditions"""
        return execute(
            "UPDATE " + self.__class__.__name__ + " SET " + ", ".join([f"{k} = ?" for k in new_values]) + 
            " WHERE " + " AND ".join([f"{k} = ?" for k in where_conditions]),
            list(new_values.values()) + list(where_conditions.values())
        )


# Entity Models (with id)
class Recruiters(DataModel):
    username: str
    email: str
    password: str


class Companies(DataModel):
    username: str
    companyName: str
    companyPhone: str
    companyAddress: str
    companyDescription: str
    employeeSize: int = 1


class JobPosts(DataModel):
    recruiterId: int
    companyId: int
    title: str
    description: str
    experience: int
    jobType: str  # 'FULL_TIME', 'PART_TIME', 'CONTRACT', 'INTERNSHIP', 'FREELANCE'
    location: str
    salary: float
    postedOn: Optional[str] = None  # Will be auto-set by database
    validTill: str
    isActive: bool = True

    def insert(self):
        # Exclude auto-generated fields including postedOn
        data = self.model_dump(exclude={"id", "createdAt", "updatedAt", "postedOn"})
        return execute(insertQueries[self.tableName], list(data.values()))


class Skills(DataModel):
    skill: str
    # Inherits id, createdAt, updatedAt from DataModel


class Freelancers(DataModel):
    username: str
    email: str
    password: str


class FreelancerDetails(DataModel):
    freelancerId: int
    firstName: str
    middleName: str
    lastName: str
    phoneNumber: str
    contactEmail: str
    about: str
    dateOfBirth: str
    address: str


class Experiences(DataModel):
    freelancerId: int
    companyName: str
    startDate: str
    endDate: Optional[str] = None  # NULL for current positions
    role: str
    description: Optional[str] = None


class Educations(DataModel):
    freelancerId: int
    course: str
    degree: str
    school: str
    startDate: str
    endDate: str
    cgpa: float


class Resumes(DataModel):
    freelancerId: int
    name: str
    pdfData: bytes
    fileSize: int
    isDefault: bool = False
    uploadedAt: Optional[str] = None  # Will be auto-set by database

    def insert(self):
        # Exclude auto-generated fields including uploadedAt
        data = self.model_dump(exclude={"id", "createdAt", "updatedAt", "uploadedAt"})
        return execute(insertQueries[self.tableName], list(data.values()))


# Junction Models (without id)
class PostSkills(JunctionModel):
    postId: int
    skillId: int
    isRequired: bool = True


class RecruiterCompanies(JunctionModel):
    recruiterId: int
    companyId: int
    role: str = "RECRUITER"  # 'RECRUITER', 'ADMIN', 'HR_MANAGER'
    joinedAt: Optional[str] = None  # Will be auto-set by database
    isActive: bool = True

    def insert(self):
        # Exclude auto-generated fields including joinedAt
        data = self.model_dump(exclude={"createdAt", "joinedAt"})
        return execute(insertQueries[self.tableName], list(data.values()))


class FreelancerSkills(JunctionModel):
    freelancerId: int
    skillId: int
    proficiencyLevel: str = "BEGINNER"  # 'BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT'
    yearsOfExperience: int = 0


class Applications(DataModel):  # Changed from JunctionModel to DataModel
    """
    Changed to DataModel since Applications needs audit trails and tracking.
    Composite primary key handled at SQL level.
    """
    jobPostId: int
    freelancerId: int
    status: str = "PENDING"  # 'PENDING', 'UNDER_REVIEW', 'SHORTLISTED', 'INTERVIEWED', 'ACCEPTED', 'REJECTED', 'WITHDRAWN'
    appliedOn: Optional[str] = None  # Will be auto-set by database
    resumeId: int
    coverLetter: Optional[str] = None
    createdAt: Optional[str] = None  # Will be auto-set by database
    updatedAt: Optional[str] = None  # Will be auto-set by database

    def insert(self):
        # Exclude all auto-generated fields for Applications
        data = self.model_dump(exclude={"id", "createdAt", "updatedAt", "appliedOn"})
        return execute(insertQueries[self.tableName], list(data.values()))