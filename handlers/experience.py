from .db import DB
from models import Experience

class ExperienceHandler:
    def create(self, experience: Experience):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO experience (freelancerId, company, role, startDate, endDate, description) VALUES (?, ?, ?, ?, ?, ?)",
                (experience.freelancerId, experience.companyName, experience.role, experience.startDate, experience.endDate, experience.description)
            )
            newExperienceId = cursor.lastrowid
            connection.commit()
            return newExperienceId

    def get(self, experienceId):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM experience WHERE experienceId = ?", (experienceId,))
            row = cursor.fetchone()

            if row is None:
                return None

            return Experience(
                id=row[0],
                freelancerId=row[1],
                companyName=row[2],
                role=row[3],
                startDate=row[4],
                endDate=row[5],
                description=row[6]
            )
    
    def get_experiences(self, freelancerId: int):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM experience WHERE freelancerId = ?",
                (freelancerId,)
            )
            rows = cursor.fetchall()
            return [Experience(
                id=row[0],
                freelancerId=row[1],
                companyName=row[2],
                role=row[3],
                startDate=row[4],
                endDate=row[5],
                description=row[6]
            ) for row in rows]
    
    def update(self, experience: Experience):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE experience SET freelancerId = ?, company = ?, role = ?, startDate = ?, endDate = ?, description = ? WHERE experienceId = ?",
                (experience.freelancerId, experience.companyName, experience.role, experience.startDate, experience.endDate, experience.description, experience.id)
            )
            connection.commit()
            return True
    
    def delete(self, experienceId):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("DELETE FROM experience WHERE experienceId = ?", (experienceId,))
            connection.commit()
            return True