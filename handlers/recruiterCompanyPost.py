from models import RecruiterCompanyPost
from .db import DB


class RecruiterCompanyPostHandler:
    def create(self, recruiterCompanyPost: RecruiterCompanyPost):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO recruiterCompanyPosts (recruiterId, companyId, postId, postedOn, validTill) VALUES (?, ?, ?, ?, ?)",
                (recruiterCompanyPost.recruiterId, recruiterCompanyPost.companyId, recruiterCompanyPost.postId, recruiterCompanyPost.postedOn, recruiterCompanyPost.validTill)
            )
            connection.commit()
            return True
    
    
    def get_posts(self, recruiterId = "", companyId = ""):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            
            if "" in [recruiterId, companyId]:
                cursor.execute("SELECT * FROM recruiterCompanyPosts WHERE recruiterId = ? OR companyId = ?", (recruiterId, companyId))
            else:
                cursor.execute("SELECT * FROM recruiterCompanyPosts WHERE recruiterId = ? AND companyId = ?", (recruiterId, companyId))
        
            res = cursor.fetchall()
            return [RecruiterCompanyPost(recruiterId=row[1], companyId=row[2], postId=row[3], postedOn=row[4], validTill=row[5]) for row in res]
        
    def remove(self, recruiterId, companyId, postId):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("DELETE FROM recruiterCompanyPosts WHERE recruiterId = ? AND companyId = ? AND postId = ?", (recruiterId, companyId, postId))
            connection.commit()
            return True

    def get_post(self, postId):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM recruiterCompanyPosts WHERE postId = ?", (postId,))
            row = cursor.fetchone()

            if row is None:
                return None

            return RecruiterCompanyPost(
                recruiterId = row[1],
                companyId = row[2],
                postId = row[3],
                postedOn = row[4],
                validTill = row[5]
            )