import sqlite3
from . import models
from . import utils


class DB:
    def __init__(self, db_file):
        self.db_file = db_file
        self.connection = None
    
    def connect(self):
        self.connection = sqlite3.connect(self.db_file)
        return self
    
    def close(self):
        self.connection.close()
        return self
    
    def commit(self):
        self.connection.commit()
        return self
    
    def execute(self, query, params=None, commit=True):
        
        if self.connection is None:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        
        if commit:
            self.commit()

        return cursor

    def __enter__(self):
        if self.connection is None:
            self.connect()    
        return self.connection.cursor()
    

    def __del__(self):
        if self.connection is not None:
            self.close()
            self.connection = None
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        self.connection = None


class UserHandler:
    def create_user(self, user: models.User) -> models.User:
        with DB() as cursor:
            cursor.execute(
                "INSERT INTO users (username, email, password, user_type) VALUES (?, ?, ?, ?)",
                (user.userId, user.email, user.password, user.userType)
            )
            newUserId = cursor.lastrowid
            cursor.commit()
            user.userId = newUserId

            return user


    def get_user(self, user_id: int) -> models.User:
        with DB() as cursor:
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
    
    def update_user(self, user: models.User) -> models.User:
        with DB() as cursor:
            cursor.execute(
                "UPDATE users SET username = ?, email = ?, password = ?, user_type = ? WHERE userId = ?",
                (user.username, user.email, user.password, user.userType, user.userId)
            )
            cursor.commit()
            return user

    def delete_user(self, user_id: int) -> models.User | None:
        with DB() as cursor:
            cursor.execute(
                "DELETE FROM users WHERE userId = ?",
                (user_id,)
            )
            cursor.commit()
            return self.get_user(user_id)


    def match_password(self, user_id: int, password: str) -> bool:
        with DB() as cursor:
            cursor.execute(
                "SELECT password FROM users WHERE userId = ?",
                (user_id,)
            )
            row = cursor.fetchone()

            if row is None:
                return False

            return utils.hash_password(password) == row[0]
        

    def get_user_type(self, user_id: int) -> models.UserType:
        with DB() as cursor:
            cursor.execute(
                "SELECT user_type FROM users WHERE userId = ?",
                (user_id,)
            )
            row = cursor.fetchone()

            if row is None:
                return None
            return models.UserType(row[0])
        

    def get_user_id(self, email: str | None = None, username: str | None = None) -> int:
        with DB() as cursor:
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
    def get_freelancer_profile(self, user_id: int) -> models.FreelancerProfile | None:
        with DB() as cursor:
            cursor.execute(
                "SELECT * FROM freelancer_profiles WHERE userId = ?",
                (user_id,)
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return models.FreelancerProfile(
                userId=row[0],
                firstName=row[1],
                lastName=row[2],
                education=row[3],
                experience=row[4],
                skills=row[5]
            )

    def update_freelancer_profile(self, user_id: int, profile: models.FreelancerProfile) -> models.FreelancerProfile:
        with DB() as cursor:
            cursor.execute(
                "UPDATE freelancer_profiles SET firstName = ?, lastName = ?, education = ?, experience = ?, skills = ? WHERE userId = ?",
                (profile.firstName, profile.lastName, profile.education, profile.experience, profile.skills, user_id)
            )
            cursor.commit()
            return profile

    def delete_freelancer_profile(self, user_id: int) -> models.FreelancerProfile:
        with DB() as cursor:
            cursor.execute(
                "DELETE FROM freelancer_profiles WHERE userId = ?",
                (user_id,)
            )
            cursor.commit()
            return self.get_freelancer_profile(user_id)


    # --------------------------
    # User Skill Handler
    # --------------------------
    def get_skills(self, user_id: int) -> List[models.Skill]:
        return UserSkillHandler().get_user_skills(user_id)

    def add_skill(self, user_id: int, skill: str) -> models.Skill:
        return UserSkillHandler().add_user_skill(user_id, skill)

    def remove_skill(self, user_id: int, skill_id: int) -> models.Skill:
        return UserSkillHandler().remove_user_skill(user_id, skill_id)

    
    # --------------------------
    # User Experience Handler
    # --------------------------
    def get_experiences(self, user_id: int) -> List[models.Experience] | None:
        with DB() as cursor:
            cursor.execute(
                "SELECT * FROM experiences WHERE userId = ?",
                (user_id,)
            )
            rows = cursor.fetchall()

            return [models.Experience(experienceId=row[0], company=row[1], position=row[2], startDate=row[3], endDate=row[4], description=row[5]) for row in rows]

    def add_experience(self, user_id: int, experience: models.Experience) -> models.Experience:
        with DB() as cursor:
            cursor.execute(
                "INSERT INTO experiences (userId, company, position, startDate, endDate, description) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, experience.company, experience.position, experience.startDate, experience.endDate, experience.description)
            )
            cursor.commit()
            return experience

    def remove_experience(self, user_id: int, experience_id: int) -> models.Experience:
        with DB() as cursor:
            cursor.execute(
                "DELETE FROM experiences WHERE userId = ? AND experienceId = ?",
                (user_id, experience_id)
            )
            cursor.commit()
            return models.Experience(experienceId=experience_id)


    # --------------------------
    # User Education Handler
    # --------------------------
    def get_educations(self, user_id: int) -> List[models.Education] | None:
        with DB() as cursor:
            cursor.execute(
                "SELECT * FROM educations WHERE userId = ?",
                (user_id,)
            )
            rows = cursor.fetchall()

            return [models.Education(educationId=row[0], school=row[1], degree=row[2], fieldOfStudy=row[3], startDate=row[4], endDate=row[5], cgpa=row[6]) for row in rows]
    
    def add_education(self, user_id: int, education: models.Education) -> models.Education:
        with DB() as cursor:
            cursor.execute(
                "INSERT INTO educations (userId, school, degree, fieldOfStudy, startDate, endDate, cgpa) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, education.school, education.degree, education.fieldOfStudy, education.startDate, education.endDate, education.cgpa)
            )
            cursor.commit()
            return education

    def remove_education(self, user_id: int, education_id: int) -> models.Education:
        with DB() as cursor:
            cursor.execute(
                "DELETE FROM educations WHERE userId = ? AND educationId = ?",
                (user_id, education_id)
            )
            cursor.commit()
            return models.Education(educationId=education_id)


class SkillHandler:
    def get_skills(self) -> List[models.Skill]:
        with DB() as cursor:
            cursor.execute(
                "SELECT * FROM skills"
            )
            rows = cursor.fetchall()

            return [models.Skill(skillId=row[0], skill=row[1]) for row in rows]

    def get_skill(self, skill_id: int) -> models.Skill | None:
        with DB() as cursor:
            cursor.execute(
                "SELECT * FROM skills WHERE skillId = ?",
                (skill_id,)
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return models.Skill(skillId=row[0], skill=row[1])

    def create_skill(self, skill: str) -> models.Skill:
        with DB() as cursor:
            cursor.execute(
                "INSERT INTO skills (skill) VALUES (?)",
                (skill,)
            )
            newSkillId = cursor.lastrowid
            cursor.commit()
            return models.Skill(skillId=newSkillId, skill=skill)

    def delete_skill(self, skill_id: int) -> models.Skill:
        with DB() as cursor:
            cursor.execute(
                "DELETE FROM skills WHERE skillId = ?",
                (skill_id,)
            )
            cursor.commit()
            return self.get_skill(skill_id)

    def get_skill_id(self, skill: str) -> int:
        with DB() as cursor:
            cursor.execute(
                "SELECT skillId FROM skills WHERE skill = ?",
                (skill,)
            )
            row = cursor.fetchone()

            if row is None:
                created_skill = self.create_skill(skill)
                return created_skill.skillId
            
            return row[0]


class UserSkillHandler:
    def get_user_skills(self, user_id: int) -> List[models.UserSkill]:
        with DB() as cursor:
            cursor.execute(
                "SELECT * FROM user_skills WHERE userId = ?",
                (user_id,)
            )
            rows = cursor.fetchall()

            return [models.UserSkill(userId=row[0], skillId=row[1]) for row in rows]
    
    def add_user_skill(self, user_id: int, skill: str) -> models.UserSkill:
        with DB() as cursor:
            skill_id = SkillHandler().get_skill_id(skill)
            cursor.execute(
                "INSERT INTO user_skills (userId, skillId) VALUES (?, ?)",
                (user_id, skill_id)
            )
            cursor.commit()
            return models.UserSkill(userId=user_id, skillId=skill_id)
    
    def remove_user_skill(self, user_id: int, skill_id: int) -> models.UserSkill:
        with DB() as cursor:
            cursor.execute(
                "DELETE FROM user_skills WHERE userId = ? AND skillId = ?",
                (user_id, skill_id)
            )
            cursor.commit()
            return models.UserSkill(userId=user_id, skillId=skill_id)

    def remove_user_skills(self, user_id: int) -> None:
        with DB() as cursor:
            cursor.execute(
                "DELETE FROM user_skills WHERE userId = ?",
                (user_id,)
            )
            cursor.commit()


class SessionHandler:
    def create_session(self, session: models.Session) -> models.Session:
        with DB() as cursor:
            cursor.execute(
                "INSERT INTO sessions (sessionId, userId) VALUES (?, ?)",
                (session.sessionId, session.userId)
            )
            cursor.commit()
            return session

    def get_session(self, session_id: str) -> models.Session | None:
        with DB() as cursor:
            cursor.execute(
                "SELECT * FROM sessions WHERE sessionId = ?",
                (session_id,)
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return models.Session(sessionId=row[0], userId=row[1])

    def delete_session(self, session_id: str) -> models.Session:
        with DB() as cursor:
            cursor.execute(
                "DELETE FROM sessions WHERE sessionId = ?",
                (session_id,)
            )
            cursor.commit()
            return self.get_session(session_id)

    def cleanup_sessions(self) -> None:
        with DB() as cursor:
            cursor.execute(
                "DELETE FROM sessions",
            )
            cursor.commit()