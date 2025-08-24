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

-- Freelancer Profile Table
CREATE TABLE IF NOT EXISTS freelancer_profiles (
    userId INTEGER PRIMARY KEY,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL,
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
                    (user.username, user.email, user.password, user.userType)
                )
                newUserId = cursor.lastrowid
                connection.commit()
                
                if newUserId is None:
                    return None
                
                user.userId = newUserId
                return user
            except sqlite3.IntegrityError:
                return None

    def get_user(self, user_id: int) -> models.User | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE userId = ?",
                (user_id,)
            )
            row = cursor.fetchone()

            if row is None:
                return None
            
            return models.User(
                userId=row[0],
                username=row[1],
                email=row[2],
                password=row[3],
                userType=row[4]
            )
    
    def update_user(self, user: models.User) -> models.User | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "UPDATE users SET username = ?, email = ?, password = ?, user_type = ? WHERE userId = ?",
                    (user.username, user.email, user.password, user.userType, user.userId)
                )
                connection.commit()
                return user
            except sqlite3.IntegrityError:
                return None

    def delete_user(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if user is None:
            return False
            
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM users WHERE userId = ?",
                (user_id,)
            )
            connection.commit()
            return cursor.rowcount > 0

    def match_password(self, user_id: int, password: str) -> bool:
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "SELECT password FROM users WHERE userId = ?",
                (user_id,)
            )
            row = cursor.fetchone()

            if row is None:
                return False

            return utils.hash_password(password) == row[0]
        
    def get_user_type(self, user_id: int) -> models.UserType | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT user_type FROM users WHERE userId = ?",
                (user_id,)
            )
            row = cursor.fetchone()

            if row is None:
                return None
            
            return row[0] if row[0] in ['FREELANCER', 'RECRUITER'] else None
        
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

    # --------------------------
    # Freelancer Profile Handler
    # --------------------------
    def create_freelancer_profile(self, profile: models.FreelancerProfile) -> models.FreelancerProfile | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO freelancer_profiles (userId, firstName, lastName) VALUES (?, ?, ?)",
                    (profile.userId, profile.firstName, profile.lastName)
                )
                connection.commit()
                return profile
            except sqlite3.IntegrityError:
                return None

    def get_freelancer_profile(self, user_id: int) -> models.FreelancerProfile | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM freelancer_profiles WHERE userId = ?",
                (user_id,)
            )
            row = cursor.fetchone()

            if row is None:
                return None

            # Get related data
            education = self.get_educations(user_id) or []
            experience = self.get_experiences(user_id) or []
            skills = self.get_user_skills_with_names(user_id) or []

            return models.FreelancerProfile(
                userId=row[0],
                firstName=row[1],
                lastName=row[2],
                education=education,
                experience=experience,
                skills=skills
            )

    def update_freelancer_profile(self, profile: models.FreelancerProfile) -> models.FreelancerProfile | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "UPDATE freelancer_profiles SET firstName = ?, lastName = ? WHERE userId = ?",
                    (profile.firstName, profile.lastName, profile.userId)
                )
                connection.commit()
                return profile
            except sqlite3.IntegrityError:
                return None

    def delete_freelancer_profile(self, user_id: int) -> bool:
        profile = self.get_freelancer_profile(user_id)
        if profile is None:
            return False
            
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM freelancer_profiles WHERE userId = ?",
                (user_id,)
            )
            connection.commit()
            return cursor.rowcount > 0

    # --------------------------
    # User Skill Handler
    # --------------------------
    def get_skills(self, user_id: int) -> List[models.UserSkill] | None:
        return UserSkillHandler().get_user_skills(user_id)

    def get_user_skills_with_names(self, user_id: int) -> List[models.Skill] | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                """SELECT s.skillId, s.skill 
                   FROM skills s 
                   JOIN user_skills us ON s.skillId = us.skillId 
                   WHERE us.userId = ?""",
                (user_id,)
            )
            rows = cursor.fetchall()
            return [models.Skill(skillId=row[0], skill=row[1]) for row in rows]

    def add_skill(self, user_id: int, skill: str) -> models.UserSkill | None:
        return UserSkillHandler().add_user_skill(user_id, skill)

    def remove_skill(self, user_id: int, skill_id: int) -> bool:
        return UserSkillHandler().remove_user_skill(user_id, skill_id)
    
    # --------------------------
    # User Experience Handler
    # --------------------------
    def get_experiences(self, user_id: int) -> List[models.Experience] | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM experience WHERE userId = ?",
                (user_id,)
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

    def add_experience(self, user_id: int, experience: models.Experience) -> models.Experience | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO experience (userId, company, position, startDate, endDate, description) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, experience.company, experience.position, experience.startDate, experience.endDate, experience.description)
                )
                newExperienceId = cursor.lastrowid
                connection.commit()
                
                if newExperienceId is not None:
                    experience.experienceId = newExperienceId
                    experience.userId = user_id
                    
                return experience
            except sqlite3.IntegrityError:
                return None

    def remove_experience(self, user_id: int, experience_id: int) -> bool:
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM experience WHERE userId = ? AND experienceId = ?",
                (user_id, experience_id)
            )
            connection.commit()
            return cursor.rowcount > 0

    # --------------------------
    # User Education Handler
    # --------------------------
    def get_educations(self, user_id: int) -> List[models.Education] | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM education WHERE userId = ?",
                (user_id,)
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
    
    def add_education(self, user_id: int, education: models.Education) -> models.Education | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO education (userId, school, degree, fieldOfStudy, startDate, endDate, cgpa) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (user_id, education.school, education.degree, education.fieldOfStudy, education.startDate, education.endDate, education.cgpa)
                )
                newEducationId = cursor.lastrowid
                connection.commit()
                
                if newEducationId is not None:
                    education.educationId = newEducationId
                    education.userId = user_id
                    
                return education
            except sqlite3.IntegrityError:
                return None

    def remove_education(self, user_id: int, education_id: int) -> bool:
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM education WHERE userId = ? AND educationId = ?",
                (user_id, education_id)
            )
            connection.commit()
            return cursor.rowcount > 0


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
    def get_user_skills(self, user_id: int) -> List[models.UserSkill] | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM user_skills WHERE userId = ?",
                (user_id,)
            )
            rows = cursor.fetchall()
            return [models.UserSkill(userId=row[0], skillId=row[1]) for row in rows]
    
    def add_user_skill(self, user_id: int, skill: str) -> models.UserSkill | None:
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
                    (user_id, skill_id)
                )
                connection.commit()
                return models.UserSkill(userId=user_id, skillId=skill_id)
            except sqlite3.IntegrityError:
                return None
    
    def remove_user_skill(self, user_id: int, skill_id: int) -> bool:
        with DB() as connection:
            if not connection:
                return False
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM user_skills WHERE userId = ? AND skillId = ?",
                (user_id, skill_id)
            )
            connection.commit()
            return cursor.rowcount > 0

    def remove_user_skills(self, user_id: int) -> None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM user_skills WHERE userId = ?",
                (user_id,)
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