from .db import DB
from models import PostSkill


class PostSkillHandler:
    def create(self, postSkill: PostSkill):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("INSERT INTO postSkills (postId, skillId) VALUES (?, ?)", (postSkill.postId, postSkill.skillId))
            connection.commit()
            return True
    
    def remove(self, postSkill: PostSkill):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("DELETE FROM postSkills WHERE postId = ? and skillId = ?", (postSkill.postId, postSkill.skillId))
            connection.commit()
            return True
    
    def get_posts_by_skill_id(self, skillId):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM postSkills WHERE skillId = ?", (skillId,))
            res = cursor.fetchall()
            return [PostSkill(postId=row[1], skillId=row[2]) for row in res]
    
    def get_skills_by_post_id(self, postId):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM postSkills WHERE postId = ?", (postId,))
            res = cursor.fetchall()
            return [PostSkill(postId=row[1], skillId=row[2]) for row in res]
    