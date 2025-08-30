from .db import DB
from models import Application


class ApplicationHandler:
    def create(self, application: Application):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("INSERT INTO applications (freelancerId, jobPostId) VALUES (?, ?)", (application.freelancerId, application.jobPostId))
            connection.commit()
            return True
    
    def delete(self, freelancerId):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("DELETE FROM applications WHERE freelancerId = ?", (freelancerId,))
            connection.commit()
            return cursor.rowcount
    
    def get_applications(self, freelancerId):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT jobId FROM applications WHERE freelancerId = ?", (freelancerId,))
            rows = cursor.fetchall()
            return [row[0] for row in rows]
    
    def get_applications_by_job(self, jobId):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT freelancerId FROM applications WHERE jobId = ?", (jobId,))
            rows = cursor.fetchall()
            return [row[0] for row in rows]