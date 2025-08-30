from .db import DB
from models import FreelancerSkill


class FreelancerSkillHandler:
    def create(self, freelancerSkill: FreelancerSkill):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("INSERT INTO freelancerSkills (freelancerId, skillId) VALUES (?, ?)", (freelancerSkill.freelancerId, freelancerSkill.skillId))
            connection.commit()
            return True
    
    def get_freelancer_skills(self, freelancerId):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT skillId FROM freelancerSkills WHERE freelancerId = ?", (freelancerId,))
            rows = cursor.fetchall()
            return [row[0] for row in rows]
    
    def remove(self, freelancerSkill: FreelancerSkill):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("DELETE FROM freelancerSkills WHERE freelancerId = ? and skillId = ?", (freelancerSkill.freelancerId, freelancerSkill.skillId))
            connection.commit()
            return True
    
    def delete(self, freelancerId):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("DELETE FROM freelancerSkills WHERE freelancerId = ?", (freelancerId,))
            connection.commit()
            return cursor.rowcount