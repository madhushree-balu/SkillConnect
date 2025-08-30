from .db import DB
from models import JobPost


class JobPostHandler:
    def __init__(self):
        self.db = DB()
    
    def create(self, job_post: JobPost):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO job_posts (title, description, experience, jobType, location, salary) VALUES (?, ?, ?, ?, ?, ?)",
                (job_post.title, job_post.description, job_post.experience, job_post.jobType, job_post.location, job_post.salary)
            )
            connection.commit()
            return cursor.lastrowid
    
    def update(self, job_post: JobPost):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE job_posts SET title = ?, description = ?, location = ?, salary = ?, experience = ?, jobType = ? WHERE id = ?",
                (job_post.title, job_post.description, job_post.location, job_post.salary, job_post.experience, job_post.jobType, job_post.id)
            )
            connection.commit()
            return job_post

    
    def get_job_post(self, id):
        res = self.db.execute("SELECT * FROM job_posts WHERE id = ?", (id,)).fetchone()
        if res is None:
            return None
        return JobPost(
            id=res[0],
            title=res[1],
            description=res[2],
            experience=res[3],
            jobType=res[4],
            location=res[5],
            salary=res[6],
        )
    
    def get_all_jobs(self):
        res = self.db.execute("SELECT * FROM job_posts").fetchall()
        return [JobPost(
            id=row[0],
            title=row[1],
            description=row[2],
            experience=row[3],
            jobType=row[4],
            location=row[5],
            salary=row[6],
        ) for row in res]