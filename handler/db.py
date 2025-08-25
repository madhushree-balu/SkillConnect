from typing import List
import sqlite3
from . import models
from . import utils


create_table_commands = """
-- Core User & Session Tables
CREATE TABLE IF NOT EXISTS users (
    userId INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    user_type TEXT NOT NULL CHECK (user_type IN ('FREELANCER', 'RECRUITER'))
);

CREATE TABLE IF NOT EXISTS sessions (
    sessionId TEXT PRIMARY KEY,
    userId INTEGER NOT NULL,
    FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_profiles (
    userId INTEGER PRIMARY KEY,
    firstName TEXT NOT NULL,
    middleName TEXT,
    lastName TEXT NOT NULL,
    summary TEXT DEFAULT '',
    phoneNumber TEXT DEFAULT '',
    address TEXT DEFAULT '',
    personalWebsite TEXT DEFAULT '',
    contactEmail TEXT DEFAULT '',
    FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
);

-- Education Table
CREATE TABLE IF NOT EXISTS education (
    educationId INTEGER PRIMARY KEY AUTOINCREMENT,
    userId INTEGER NOT NULL,
    school TEXT NOT NULL,
    degree TEXT NOT NULL,
    fieldOfStudy TEXT NOT NULL,
    startDate TEXT NOT NULL,
    endDate TEXT,
    cgpa REAL,
    FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
);

-- Experience Table
CREATE TABLE IF NOT EXISTS experience (
    experienceId INTEGER PRIMARY KEY AUTOINCREMENT,
    userId INTEGER NOT NULL,
    company TEXT NOT NULL,
    position TEXT NOT NULL,
    startDate TEXT NOT NULL,
    endDate TEXT,
    description TEXT,
    FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
);

-- Skills Table
CREATE TABLE IF NOT EXISTS skills (
    skillId INTEGER PRIMARY KEY AUTOINCREMENT,
    skill TEXT NOT NULL UNIQUE
);

-- User Skills Junction Table
CREATE TABLE IF NOT EXISTS user_skills (
    userId INTEGER NOT NULL,
    skillId INTEGER NOT NULL,
    PRIMARY KEY (userId, skillId),
    FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE,
    FOREIGN KEY (skillId) REFERENCES skills(skillId) ON DELETE CASCADE
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_sessions_userId ON sessions(userId);
CREATE INDEX IF NOT EXISTS idx_education_userId ON education(userId);
CREATE INDEX IF NOT EXISTS idx_experience_userId ON experience(userId);
CREATE INDEX IF NOT EXISTS idx_user_skills_userId ON user_skills(userId);
CREATE INDEX IF NOT EXISTS idx_user_skills_skillId ON user_skills(skillId);
"""


class DB:
    def __init__(self, db_file="storage.sqlite3"):
        self.db_file = db_file
        self.connection: sqlite3.Connection | None = None
    
    def connect(self):
        self.connection = sqlite3.connect(self.db_file)
        return self
    
    def close(self):
        if self.connection is not None:
            self.connection.close()
        return self
    
    def commit(self):
        if self.connection is not None:
            self.connection.commit()
        return self
    
    def execute(self, query, params: tuple = tuple(), commit=True):
        if self.connection is None:
            self.connect()
        
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            if commit:
                self.commit()

            return cursor

    def create_tables(self):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.executescript(create_table_commands)
            connection.commit()
            create_additional_tables()
        
    
    def __enter__(self):
        if self.connection is None:
            self.connect()    
        return self.connection
    
    def __del__(self):
        if self.connection is not None:
            self.close()
            self.connection = None
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        self.connection = None


class UserHandler:
    def create_user(self, user: models.User) -> models.User | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (username, email, password, user_type) VALUES (?, ?, ?, ?)",
                    (user.username, user.email, user.password)
                )
                newUserId = cursor.lastrowid
                connection.commit()
                
                if newUserId is None:
                    return None
                
                user.userId = newUserId
                return user
            except sqlite3.IntegrityError:
                return None

    def get_user(self, userId: int = -1, username: str = "") -> models.User | None:
        
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE userId = ? or username = ?",
                (userId,username)
            )
            row = cursor.fetchone()

            if row is None:
                return None
            
            return models.User(
                userId=row[0],
                username=row[1],
                email=row[2],
                password=row[3],
                
            )
    
    def update_user(self, user: models.User) -> models.User | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "UPDATE users SET username = ?, email = ?, password = ?, user_type = ? WHERE userId = ?",
                    (user.username, user.email, user.password, user.userId)
                )
                connection.commit()
                return user
            except sqlite3.IntegrityError:
                return None

    def delete_user(self, userId: int) -> bool:
        user = self.get_user(userId)
        if user is None:
            return False
            
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM users WHERE userId = ?",
                (userId,)
            )
            connection.commit()
            return cursor.rowcount > 0

    def match_password(self, userId: int, password: str) -> bool:
        print(userId, password)
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "SELECT password FROM users WHERE userId = ?",
                (userId,)
            )
            row = cursor.fetchone()

            if row is None:
                return False

            return utils.hash_password(password) == row[0]
        
        
    def get_user_id(self, email: str | None = None, username: str | None = None) -> int | None:
        if email is None and username is None:
            return None
            
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT userId FROM users WHERE email = ? OR username = ?",
                (email, username)
            )
            row = cursor.fetchone()

            if row is None:
                return None
            return row[0]
        
    # -----------
    # User Profile
    # -----------
    def create_user_profile(self, profile: models.UserProfile) -> models.UserProfile | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO user_profiles (userId, firstName, middleName, lastName, summary, phoneNumber, address, personalWebsite, contactEmail) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (profile.userId, profile.firstName, profile.middleName, profile.lastName, profile.summary, profile.phoneNumber, profile.address, profile.personalWebsite, profile.contactEmail)
                )
                connection.commit()
                return profile
            except sqlite3.IntegrityError:
                return None

    def get_user_profile(self, userId: int) -> models.UserProfile | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM user_profiles WHERE userId = ?", (userId,))
            row = cursor.fetchone()
            if row is None:
                return None
            
            return models.UserProfile(
                userId=row[0], firstName=row[1], middleName=row[2], 
                lastName=row[3], summary=row[4], phoneNumber=row[5],
                address=row[6], personalWebsite=row[7], contactEmail=row[8]
            )
    def update_user_profile(self, profile: models.UserProfile) -> models.UserProfile | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "UPDATE user_profiles SET firstName = ?, middleName = ?, lastName = ?, summary = ?, phoneNumber = ?, address = ?, personalWebsite = ?, contactEmail = ? WHERE userId = ?",
                    (profile.firstName, profile.middleName, profile.lastName, profile.summary, profile.phoneNumber, profile.address, profile.personalWebsite, profile.contactEmail, profile.userId)
                )
                connection.commit()
                return profile
            except sqlite3.IntegrityError:
                return None

    # --------------------------
    # User Skill Handler
    # --------------------------
    def get_skills(self, userId: int) -> List[models.UserSkill] | None:
        return UserSkillHandler().get_user_skills(userId)

    def get_user_skills_with_names(self, userId: int) -> List[models.Skill] | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                """SELECT s.skillId, s.skill 
                   FROM skills s 
                   JOIN user_skills us ON s.skillId = us.skillId 
                   WHERE us.userId = ?""",
                (userId,)
            )
            rows = cursor.fetchall()
            return [models.Skill(skillId=row[0], skill=row[1]) for row in rows]

    def add_skill(self, userId: int, skill: str) -> models.UserSkill | None:
        return UserSkillHandler().add_user_skill(userId, skill)

    def remove_skill(self, userId: int, skill_id: int) -> bool:
        return UserSkillHandler().remove_user_skill(userId, skill_id)
    
    # --------------------------
    # User Experience Handler
    # --------------------------
    def get_experiences(self, userId: int) -> List[models.Experience] | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM experience WHERE userId = ?",
                (userId,)
            )
            rows = cursor.fetchall()
            return [models.Experience(
                experienceId=row[0],
                userId=row[1],
                company=row[2],
                position=row[3],
                startDate=row[4],
                endDate=row[5],
                description=row[6]
            ) for row in rows]

    def add_experience(self, userId: int, experience: models.Experience) -> models.Experience | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO experience (userId, company, position, startDate, endDate, description) VALUES (?, ?, ?, ?, ?, ?)",
                    (userId, experience.company, experience.position, experience.startDate, experience.endDate, experience.description)
                )
                newExperienceId = cursor.lastrowid
                connection.commit()
                
                if newExperienceId is not None:
                    experience.experienceId = newExperienceId
                    experience.userId = userId
                    
                return experience
            except sqlite3.IntegrityError:
                return None

    def remove_experience(self, userId: int, experience_id: int) -> bool:
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM experience WHERE userId = ? AND experienceId = ?",
                (userId, experience_id)
            )
            connection.commit()
            return cursor.rowcount > 0
        
    def update_experience(self, experience: models.Experience) -> models.Experience | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "UPDATE experience SET company = ?, position = ?, startDate = ?, endDate = ?, description = ? WHERE experienceId = ?",
                    (experience.company, experience.position, experience.startDate, experience.endDate, experience.description, experience.experienceId)
                )
                connection.commit()
                return experience
            except sqlite3.IntegrityError:
                return None

    # --------------------------
    # User Education Handler
    # --------------------------
    def get_educations(self, userId: int) -> List[models.Education] | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM education WHERE userId = ?",
                (userId,)
            )
            rows = cursor.fetchall()
            return [models.Education(
                educationId=row[0],
                userId=row[1],
                school=row[2],
                degree=row[3],
                fieldOfStudy=row[4],
                startDate=row[5],
                endDate=row[6],
                cgpa=row[7]
            ) for row in rows]
    
    def add_education(self, userId: int, education: models.Education) -> models.Education | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO education (userId, school, degree, fieldOfStudy, startDate, endDate, cgpa) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (userId, education.school, education.degree, education.fieldOfStudy, education.startDate, education.endDate, education.cgpa)
                )
                newEducationId = cursor.lastrowid
                connection.commit()
                
                if newEducationId is not None:
                    education.educationId = newEducationId
                    education.userId = userId
                    
                return education
            except sqlite3.IntegrityError:
                return None

    def remove_education(self, userId: int, education_id: int) -> bool:
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM education WHERE userId = ? AND educationId = ?",
                (userId, education_id)
            )
            connection.commit()
            return cursor.rowcount > 0
    
    def update_education(self, education: models.Education) -> models.Education | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "UPDATE education SET school = ?, degree = ?, fieldOfStudy = ?, startDate = ?, endDate = ?, cgpa = ? WHERE educationId = ?",
                    (education.school, education.degree, education.fieldOfStudy, education.startDate, education.endDate, education.cgpa, education.educationId)
                )
                connection.commit()
                return education
            except sqlite3.IntegrityError:
                return None


class SkillHandler:
    def get_skills(self) -> List[models.Skill] | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM skills"
            )
            rows = cursor.fetchall()
            return [models.Skill(skillId=row[0], skill=row[1]) for row in rows]

    def get_skill(self, skill_id: int) -> models.Skill | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM skills WHERE skillId = ?",
                (skill_id,)
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return models.Skill(skillId=row[0], skill=row[1])

    def create_skill(self, skill: str) -> models.Skill | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO skills (skill) VALUES (?)",
                    (skill,)
                )
                newSkillId = cursor.lastrowid
                if newSkillId is None:
                    return None
                connection.commit()
                return models.Skill(skillId=newSkillId, skill=skill)
            except sqlite3.IntegrityError:
                return None

    def delete_skill(self, skill_id: int) -> bool:
        skill = self.get_skill(skill_id)
        if skill is None:
            return False
            
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM skills WHERE skillId = ?",
                (skill_id,)
            )
            connection.commit()
            return cursor.rowcount > 0

    def get_skill_id(self, skill: str) -> int | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT skillId FROM skills WHERE skill = ?",
                (skill,)
            )
            row = cursor.fetchone()

            if row is None:
                created_skill = self.create_skill(skill)
                if created_skill is None:
                    return None
                return created_skill.skillId
            
            return row[0]


class UserSkillHandler:
    def get_user_skills(self, userId: int) -> List[models.UserSkill] | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM user_skills WHERE userId = ?",
                (userId,)
            )
            rows = cursor.fetchall()
            return [models.UserSkill(userId=row[0], skillId=row[1]) for row in rows]
    
    def add_user_skill(self, userId: int, skill: str) -> models.UserSkill | None:
        skill_id = SkillHandler().get_skill_id(skill)
        if not skill_id:
            return None
            
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO user_skills (userId, skillId) VALUES (?, ?)",
                    (userId, skill_id)
                )
                connection.commit()
                return models.UserSkill(userId=userId, skillId=skill_id)
            except sqlite3.IntegrityError:
                return None
    
    def remove_user_skill(self, userId: int, skill_id: int) -> bool:
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM user_skills WHERE userId = ? AND skillId = ?",
                (userId, skill_id)
            )
            connection.commit()
            return cursor.rowcount > 0

    def remove_user_skills(self, userId: int) -> None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM user_skills WHERE userId = ?",
                (userId,)
            )
            connection.commit()


class SessionHandler:
    def create_session(self, session: models.Session) -> models.Session | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO sessions (sessionId, userId) VALUES (?, ?)",
                    (session.sessionId, session.userId)
                )
                connection.commit()
                return session
            except sqlite3.IntegrityError:
                return None

    def get_session(self, session_id: str) -> models.Session | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM sessions WHERE sessionId = ?",
                (session_id,)
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return models.Session(sessionId=row[0], userId=row[1])

    def delete_session(self, session_id: str) -> bool:
        session = self.get_session(session_id)
        if session is None:
            return False
            
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM sessions WHERE sessionId = ?",
                (session_id,)
            )
            connection.commit()
            return cursor.rowcount > 0

    def cleanup_sessions(self) -> None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("DELETE FROM sessions")
            connection.commit()
            
            

additional_create_table_commands = """
-- Recruiter Tables
CREATE TABLE IF NOT EXISTS recruiters (
    recruiterId INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    company TEXT DEFAULT '',
    location TEXT DEFAULT '',
    website TEXT DEFAULT '',
    contact_email TEXT DEFAULT '',
    contact_number TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS recruiter_sessions (
    sessionId TEXT PRIMARY KEY,
    recruiterId INTEGER NOT NULL,
    FOREIGN KEY (recruiterId) REFERENCES recruiters(recruiterId) ON DELETE CASCADE
);

-- Job Tables
CREATE TABLE IF NOT EXISTS job_posts (
    jobId INTEGER PRIMARY KEY AUTOINCREMENT,
    recruiterId INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    location TEXT DEFAULT '',
    salary REAL DEFAULT 0.0,
    experience INTEGER DEFAULT 0,
    FOREIGN KEY (recruiterId) REFERENCES recruiters(recruiterId) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS job_skills (
    jobId INTEGER NOT NULL,
    skillId INTEGER NOT NULL,
    PRIMARY KEY (jobId, skillId),
    FOREIGN KEY (jobId) REFERENCES job_posts(jobId) ON DELETE CASCADE,
    FOREIGN KEY (skillId) REFERENCES skills(skillId) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS job_applications (
    jobId INTEGER NOT NULL,
    freelancerId INTEGER NOT NULL,
    applicationDate TEXT DEFAULT '',
    resumeId INTEGER DEFAULT -1,
    PRIMARY KEY (jobId, freelancerId),
    FOREIGN KEY (jobId) REFERENCES job_posts(jobId) ON DELETE CASCADE,
    FOREIGN KEY (freelancerId) REFERENCES users(userId) ON DELETE CASCADE,
    FOREIGN KEY (resumeId) REFERENCES resumes(resumeId) ON DELETE SET NULL
);

-- Resume Table
CREATE TABLE IF NOT EXISTS resumes (
    resumeId INTEGER PRIMARY KEY AUTOINCREMENT,
    freelancerId INTEGER NOT NULL,
    name TEXT NOT NULL,
    pdfData BLOB NOT NULL,
    FOREIGN KEY (freelancerId) REFERENCES users(userId) ON DELETE CASCADE
);

-- Additional Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_recruiters_email ON recruiters(email);
CREATE INDEX IF NOT EXISTS idx_recruiter_sessions_recruiterId ON recruiter_sessions(recruiterId);
CREATE INDEX IF NOT EXISTS idx_job_posts_recruiterId ON job_posts(recruiterId);
CREATE INDEX IF NOT EXISTS idx_job_skills_jobId ON job_skills(jobId);
CREATE INDEX IF NOT EXISTS idx_job_skills_skillId ON job_skills(skillId);
CREATE INDEX IF NOT EXISTS idx_job_applications_jobId ON job_applications(jobId);
CREATE INDEX IF NOT EXISTS idx_job_applications_freelancerId ON job_applications(freelancerId);
CREATE INDEX IF NOT EXISTS idx_resumes_freelancerId ON resumes(freelancerId);
"""


class RecruiterHandler:
    def create_recruiter(self, recruiter: models.Recruiter) -> models.Recruiter | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO recruiters (name, email, password, company, location, website, contact_email, contact_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (recruiter.name, recruiter.email, recruiter.password, recruiter.company, recruiter.location, recruiter.website, recruiter.contact_email, recruiter.contact_number)
                )
                newRecruiterId = cursor.lastrowid
                connection.commit()
                
                if newRecruiterId is None:
                    return None
                
                recruiter.recruiterId = newRecruiterId
                return recruiter
            except sqlite3.IntegrityError:
                return None

    def get_recruiter(self, recruiterId: int = -1, email: str = "") -> models.Recruiter | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM recruiters WHERE recruiterId = ? OR email = ?",
                (recruiterId, email)
            )
            row = cursor.fetchone()

            if row is None:
                return None
            
            return models.Recruiter(
                recruiterId=row[0],
                name=row[1],
                email=row[2],
                password=row[3],
                company=row[4],
                location=row[5],
                website=row[6],
                contact_email=row[7],
                contact_number=row[8]
            )
    
    def update_recruiter(self, recruiter: models.Recruiter) -> models.Recruiter | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "UPDATE recruiters SET name = ?, email = ?, password = ?, company = ?, location = ?, website = ?, contact_email = ?, contact_number = ? WHERE recruiterId = ?",
                    (recruiter.name, recruiter.email, recruiter.password, recruiter.company, recruiter.location, recruiter.website, recruiter.contact_email, recruiter.contact_number, recruiter.recruiterId)
                )
                connection.commit()
                return recruiter
            except sqlite3.IntegrityError:
                return None

    def delete_recruiter(self, recruiterId: int) -> bool:
        recruiter = self.get_recruiter(recruiterId)
        if recruiter is None:
            return False
            
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM recruiters WHERE recruiterId = ?",
                (recruiterId,)
            )
            connection.commit()
            return cursor.rowcount > 0

    def match_password(self, recruiterId: int, password: str) -> bool:
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "SELECT password FROM recruiters WHERE recruiterId = ?",
                (recruiterId,)
            )
            row = cursor.fetchone()

            if row is None:
                return False

            return utils.hash_password(password) == row[0]

    def get_recruiter_id(self, email: str) -> int | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT recruiterId FROM recruiters WHERE email = ?",
                (email,)
            )
            row = cursor.fetchone()

            if row is None:
                return None
            return row[0]


class JobPostHandler:
    def create_job_post(self, job_post: models.JobPost) -> models.JobPost | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO job_posts (recruiterId, title, description, location, salary, experience) VALUES (?, ?, ?, ?, ?, ?)",
                    (job_post.recruiterId, job_post.title, job_post.description, job_post.location, job_post.salary, job_post.experience)
                )
                newJobId = cursor.lastrowid
                connection.commit()
                
                if newJobId is None:
                    return None
                
                job_post.jobId = newJobId
                return job_post
            except sqlite3.IntegrityError:
                return None

    def get_job_post(self, jobId: int) -> models.JobPost | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM job_posts WHERE jobId = ?",
                (jobId,)
            )
            row = cursor.fetchone()

            if row is None:
                return None
            
            return models.JobPost(
                jobId=row[0],
                recruiterId=row[1],
                title=row[2],
                description=row[3],
                location=row[4],
                salary=row[5],
                experience=row[6]
            )

    def get_job_posts_by_recruiter(self, recruiterId: int) -> List[models.JobPost] | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM job_posts WHERE recruiterId = ?",
                (recruiterId,)
            )
            rows = cursor.fetchall()
            return [models.JobPost(
                jobId=row[0],
                recruiterId=row[1],
                title=row[2],
                description=row[3],
                location=row[4],
                salary=row[5],
                experience=row[6]
            ) for row in rows]

    def get_all_job_posts(self) -> List[models.JobPost] | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM job_posts")
            rows = cursor.fetchall()
            return [models.JobPost(
                jobId=row[0],
                recruiterId=row[1],
                title=row[2],
                description=row[3],
                location=row[4],
                salary=row[5],
                experience=row[6]
            ) for row in rows]

    def update_job_post(self, job_post: models.JobPost) -> models.JobPost | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "UPDATE job_posts SET title = ?, description = ?, location = ?, salary = ?, experience = ? WHERE jobId = ?",
                    (job_post.title, job_post.description, job_post.location, job_post.salary, job_post.experience, job_post.jobId)
                )
                connection.commit()
                return job_post
            except sqlite3.IntegrityError:
                return None

    def delete_job_post(self, jobId: int) -> bool:
        job_post = self.get_job_post(jobId)
        if job_post is None:
            return False
            
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM job_posts WHERE jobId = ?",
                (jobId,)
            )
            connection.commit()
            return cursor.rowcount > 0


class JobSkillHandler:
    def add_job_skill(self, jobId: int, skill: str) -> models.JobSkills | None:
        skill_id = SkillHandler().get_skill_id(skill)
        if not skill_id:
            return None
            
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO job_skills (jobId, skillId) VALUES (?, ?)",
                    (jobId, skill_id)
                )
                connection.commit()
                return models.JobSkills(jobId=jobId, skillId=skill_id)
            except sqlite3.IntegrityError:
                return None

    def get_job_skills(self, jobId: int) -> List[models.JobSkills] | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM job_skills WHERE jobId = ?",
                (jobId,)
            )
            rows = cursor.fetchall()
            return [models.JobSkills(jobId=row[0], skillId=row[1]) for row in rows]

    def get_job_skills_with_names(self, jobId: int) -> List[models.Skill] | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                """SELECT s.skillId, s.skill 
                   FROM skills s 
                   JOIN job_skills js ON s.skillId = js.skillId 
                   WHERE js.jobId = ?""",
                (jobId,)
            )
            rows = cursor.fetchall()
            return [models.Skill(skillId=row[0], skill=row[1]) for row in rows]

    def remove_job_skill(self, jobId: int, skillId: int) -> bool:
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM job_skills WHERE jobId = ? AND skillId = ?",
                (jobId, skillId)
            )
            connection.commit()
            return cursor.rowcount > 0

    def remove_all_job_skills(self, jobId: int) -> None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM job_skills WHERE jobId = ?",
                (jobId,)
            )
            connection.commit()


class JobApplicationHandler:
    def create_application(self, application: models.JobApplications) -> models.JobApplications | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO job_applications (jobId, freelancerId, applicationDate, resumeId) VALUES (?, ?, ?, ?)",
                    (application.jobId, application.freelancerId, application.applicationDate, application.resumeId)
                )
                connection.commit()
                return application
            except sqlite3.IntegrityError:
                return None

    def get_applications_by_job(self, jobId: int) -> List[models.JobApplications] | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM job_applications WHERE jobId = ?",
                (jobId,)
            )
            rows = cursor.fetchall()
            return [models.JobApplications(
                jobId=row[0],
                freelancerId=row[1],
                applicationDate=row[2],
                resumeId=row[3]
            ) for row in rows]

    def get_applications_by_freelancer(self, freelancerId: int) -> List[models.JobApplications] | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM job_applications WHERE freelancerId = ?",
                (freelancerId,)
            )
            rows = cursor.fetchall()
            return [models.JobApplications(
                jobId=row[0],
                freelancerId=row[1],
                applicationDate=row[2],
                resumeId=row[3]
            ) for row in rows]

    def delete_application(self, jobId: int, freelancerId: int) -> bool:
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM job_applications WHERE jobId = ? AND freelancerId = ?",
                (jobId, freelancerId)
            )
            connection.commit()
            return cursor.rowcount > 0

    def check_application_exists(self, jobId: int, freelancerId: int) -> bool:
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "SELECT 1 FROM job_applications WHERE jobId = ? AND freelancerId = ?",
                (jobId, freelancerId)
            )
            return cursor.fetchone() is not None


class ResumeHandler:
    def create_resume(self, resume: models.Resume) -> models.Resume | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO resumes (freelancerId, name, pdfData) VALUES (?, ?, ?)",
                    (resume.freelancerId, resume.name, resume.pdfData)
                )
                newResumeId = cursor.lastrowid
                connection.commit()
                
                if newResumeId is None:
                    return None
                
                resume.resumeId = newResumeId
                return resume
            except sqlite3.IntegrityError:
                return None

    def get_resume(self, resumeId: int) -> models.Resume | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM resumes WHERE resumeId = ?",
                (resumeId,)
            )
            row = cursor.fetchone()

            if row is None:
                return None
            
            return models.Resume(
                resumeId=row[0],
                freelancerId=row[1],
                name=row[2],
                pdfData=row[3]
            )

    def get_resumes_by_freelancer(self, freelancerId: int) -> List[models.Resume] | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM resumes WHERE freelancerId = ?",
                (freelancerId,)
            )
            rows = cursor.fetchall()
            return [models.Resume(
                resumeId=row[0],
                freelancerId=row[1],
                name=row[2],
                pdfData=row[3]
            ) for row in rows]

    def update_resume(self, resume: models.Resume) -> models.Resume | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "UPDATE resumes SET name = ?, pdfData = ? WHERE resumeId = ?",
                    (resume.name, resume.pdfData, resume.resumeId)
                )
                connection.commit()
                return resume
            except sqlite3.IntegrityError:
                return None

    def delete_resume(self, resumeId: int) -> bool:
        resume = self.get_resume(resumeId)
        if resume is None:
            return False
            
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM resumes WHERE resumeId = ?",
                (resumeId,)
            )
            connection.commit()
            return cursor.rowcount > 0


class RecruiterSessionHandler:
    def create_session(self, session: models.RecruiterSession) -> models.RecruiterSession | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO recruiter_sessions (sessionId, recruiterId) VALUES (?, ?)",
                    (session.sessionId, session.recruiterId)
                )
                connection.commit()
                return session
            except sqlite3.IntegrityError:
                return None

    def get_session(self, sessionId: str) -> models.RecruiterSession | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM recruiter_sessions WHERE sessionId = ?",
                (sessionId,)
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return models.RecruiterSession(sessionId=row[0], recruiterId=row[1])

    def delete_session(self, sessionId: str) -> bool:
        session = self.get_session(sessionId)
        if session is None:
            return False
            
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM recruiter_sessions WHERE sessionId = ?",
                (sessionId,)
            )
            connection.commit()
            return cursor.rowcount > 0

    def cleanup_sessions(self) -> None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("DELETE FROM recruiter_sessions")
            connection.commit()

def create_additional_tables():
    with DB() as connection:
        if not connection:
            return None
        cursor = connection.cursor()
        cursor.executescript(additional_create_table_commands)
        connection.commit()