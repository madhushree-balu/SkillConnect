from models import Recruiter
from .db import DB

class RecruiterHandler:
    def get(self, recruiterId):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM recruiters WHERE recruiterId = ?", (recruiterId,))
            row = cursor.fetchone()

            if row is None:
                return None

            return Recruiter(
                id=row[0],
                username=row[1],
                email=row[2],
                password=row[3]
            )
    
    def get_recruiter_id(self, email):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT recruiterId FROM recruiters WHERE email = ?", (email,))
            row = cursor.fetchone()

            if row is None:
                return None
            return row[0]
    
    def match(self, email, password):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM recruiters WHERE email = ? AND password = ?", (email, password))
            row = cursor.fetchone()

            if row is None:
                return None

            return Recruiter(
                id=row[0],
                username=row[1],
                email=row[2],
                password=row[3]
            )
    
    def get_all_recruiters(self):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM recruiters")
            rows = cursor.fetchall()
            return [Recruiter(
                id=row[0],
                username=row[1],
                email=row[2],
                password=row[3]
            ) for row in rows]
    
    def create(self, recruiter: Recruiter):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("INSERT INTO recruiters (username, email, password) VALUES (?, ?, ?)", (recruiter.username, recruiter.email, recruiter.password))
            connection.commit()
            return cursor.lastrowid

    def update(self, recruiter: Recruiter):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("UPDATE recruiters SET username = ?, email = ?, password = ? WHERE recruiterId = ?", (recruiter.username, recruiter.email, recruiter.password, recruiter.id))
            connection.commit()
            return cursor.lastrowid
    
    def delete(self, recruiterId):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("DELETE FROM recruiters WHERE recruiterId = ?", (recruiterId,))
            connection.commit()
            return cursor.rowcount
