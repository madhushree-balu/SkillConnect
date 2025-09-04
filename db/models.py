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
        
        a = cls(**dict(data))
        return a

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
    
    # Add this enhanced search method to your JobPosts class in models.py

    @classmethod
    def search(cls, search="", page=0, min_experience=None, max_experience=None, 
            job_type=None, company_name=None, min_salary=None, max_salary=None, 
            skills=None, location=None):
        """
        Enhanced search method with multiple filters
        """
        # Build the base query with JOINs
        base_query = """
            SELECT DISTINCT jp.*, c.companyName as company_name
            FROM JobPosts jp
            LEFT JOIN Companies c ON jp.companyId = c.id
            LEFT JOIN PostSkills ps ON jp.id = ps.postId
            LEFT JOIN Skills s ON ps.skillId = s.id
            WHERE jp.isActive = 1
        """
        
        conditions = []
        params = []
        
        # Search in title and description
        if search:
            conditions.append("(jp.title LIKE ? OR jp.description LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        
        # Experience filters
        if min_experience is not None:
            conditions.append("jp.experience >= ?")
            params.append(min_experience)
        
        if max_experience is not None:
            conditions.append("jp.experience <= ?")
            params.append(max_experience)
        
        # Job type filter
        if job_type:
            conditions.append("jp.jobType = ?")
            params.append(job_type)
        
        # Company name filter
        if company_name:
            conditions.append("c.companyName LIKE ?")
            params.append(f"%{company_name}%")
        
        # Salary filters
        if min_salary is not None:
            conditions.append("jp.salary >= ?")
            params.append(min_salary)
        
        if max_salary is not None:
            conditions.append("jp.salary <= ?")
            params.append(max_salary)
        
        # Skills filter
        if skills:
            skill_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
            if skill_list:
                skill_conditions = []
                for skill in skill_list:
                    skill_conditions.append("s.skill LIKE ?")
                    params.append(f"%{skill}%")
                conditions.append(f"({' OR '.join(skill_conditions)})")
        
        # Location filter
        if location:
            conditions.append("jp.location LIKE ?")
            params.append(f"%{location}%")
        
        # Add conditions to query
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        # Add ordering and pagination
        base_query += " ORDER BY jp.postedOn DESC LIMIT ? OFFSET ?"
        params.extend([10, page * 10])  # Fixed: should be page * 10, not page * 50
        
        # Execute query
        data = fetch(base_query, params)
        
        if not data:
            return []
        
        # Convert to JobPosts objects and attach additional data
        result = []
        for row in data:
            row_dict = dict(row)
            # Store company name for template access
            company_name = row_dict.pop('company_name', None)
            
            instance = cls(**row_dict)
            
            instance = instance.model_dump()
            # Add company name as attribute
            instance['company_name'] = company_name
            
            # Get skills for this job post
            instance['skills'] = [skill['skill'] for skill in cls.get_job_skills(instance['id'])]
            
            result.append(instance)
        
        return result

    @classmethod
    def get_job_skills(cls, job_id):
        """
        Get all skills for a specific job post
        """
        skill_data = fetch("""
            SELECT s.id, s.skill, ps.isRequired
            FROM Skills s
            JOIN PostSkills ps ON s.id = ps.skillId
            WHERE ps.postId = ?
            ORDER BY ps.isRequired DESC, s.skill ASC
        """, (job_id,))
        
        if not skill_data:
            return []
        
        skills = []
        for row in skill_data:
            skill_dict = dict(row)
            skills.append(skill_dict)
        
        return skills

    @classmethod
    def get_with_company_and_skills(cls, job_id):
        """
        Get a single job post with company and skills information
        """
        job_data = fetch("""
            SELECT jp.*, c.companyName as company_name
            FROM JobPosts jp
            LEFT JOIN Companies c ON jp.companyId = c.id
            WHERE jp.id = ?
        """, (job_id,), one=True)
        
        if not job_data:
            return None
        
        row_dict = dict(job_data)
        company_name = row_dict.pop('company_name', None)
        
        instance = cls(**row_dict)
        instance = instance.model_dump()
        instance['company_name'] = company_name
        instance['skills'] = cls.get_job_skills(instance['id'])
        
        return instance

class Skills(DataModel):
    skill: str

    @classmethod
    def get_or_create(cls, skill: str):
        """
        Get an existing skill by name, or create it if it doesn't exist.
        
        Args:
            skill (str): The skill name to search for or create
            
        Returns:
            Skills: The existing or newly created Skills instance
        """
        # First, try to get the existing skill (case-insensitive search)
        existing_skill = cls.get(skill=skill)
        
        if existing_skill:
            return existing_skill
        
        # If skill doesn't exist, create a new one
        new_skill = cls(skill=skill)
        skill_id = new_skill.insert()
        
        if skill_id:
            # Return the newly created skill with the ID
            new_skill.id = skill_id
            return new_skill
        else:
            # If insertion failed, return None or raise an exception
            raise Exception(f"Failed to create skill: {skill}")

    @classmethod
    def get_by_name(cls, skill_name: str):
        """
        Get a skill by its name (case-insensitive).
        
        Args:
            skill_name (str): The skill name to search for
            
        Returns:
            Skills or None: The Skills instance if found, None otherwise
        """
        data = fetch(
            "SELECT * FROM Skills WHERE LOWER(skill) = LOWER(?)",
            (skill_name,),
            one=True
        )
        
        if not data:
            return None
            
        return cls(**dict(data))

    @classmethod
    def search_skills(cls, search_term: str, limit: int = 10):
        """
        Search for skills containing the search term.
        
        Args:
            search_term (str): The term to search for in skill names
            limit (int): Maximum number of results to return
            
        Returns:
            List[Skills]: List of matching Skills instances
        """
        data = fetch(
            "SELECT * FROM Skills WHERE skill LIKE ? ORDER BY skill LIMIT ?",
            (f"%{search_term}%", limit)
        )
        
        if not data:
            return []
            
        return [cls(**dict(row)) for row in data]

    def __str__(self):
        return f"Skill(id={self.id}, skill='{self.skill}')"

    def __repr__(self):
        return self.__str__()

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