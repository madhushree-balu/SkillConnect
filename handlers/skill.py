from .db import DB
import models

class SkillHandler:
    def __init__(self):
        self.db = DB()
        
    def get_all_skills(self):
        res = self.db.execute("SELECT * FROM skills").fetchall()
        return [models.Skill(
            id=row[0],
            skill=row[1]
        ) for row in res]
    
    def get_or_create_skill(self, skill: str) -> int | None:
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
                cursor.execute(
                    "INSERT INTO skills (skill) VALUES (?)",
                    (skill,)
                )
                connection.commit()
                return cursor.lastrowid

            return row[0]
    
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

            return models.Skill(id=row[0], skill=row[1])