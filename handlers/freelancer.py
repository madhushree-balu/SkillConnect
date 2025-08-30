from .db import DB
from models import Freelancer


class FreelancerHandler:
    def __init__(self):
        pass
    def get(self, freelancerId):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM freelancers WHERE freelancerId = ?", (freelancerId,))
            row = cursor.fetchone()

            if row is None:
                return None

            return Freelancer(
                id=row[0],
                username=row[1],
                email=row[2],
                password=row[3]
            )
    
    def match(self, email, password):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM freelancers WHERE email = ? AND password = ?", (email, password))
            row = cursor.fetchone()

            if row is None:
                return None

            return Freelancer(
                id=row[0],
                username=row[1],
                email=row[2],
                password=row[3]
            )
    
    def get_all_freelancers(self):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM freelancers")
            rows = cursor.fetchall()
            return [Freelancer(
                id=row[0],
                username=row[1],
                email=row[2],
                password=row[3]
            ) for row in rows]
    
    def get_freelancer_id(self, email):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT freelancerId FROM freelancers WHERE email = ?", (email,))
            row = cursor.fetchone()

            if row is None:
                return None
            return row[0]
    
    def create(self, freelancer: Freelancer) -> int | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("INSERT INTO freelancers (username, email, password) VALUES (?, ?, ?)", (freelancer.username, freelancer.email, freelancer.password))
            connection.commit()
            return cursor.lastrowid
    
    def update(self, freelancer: Freelancer) -> bool | None:
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("UPDATE freelancers SET username = ?, email = ?, password = ? WHERE freelancerId = ?", (freelancer.username, freelancer.email, freelancer.password, freelancer.id))
            connection.commit()
            return True
    
    
    def delete(self, freelancerId):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("DELETE FROM freelancers WHERE freelancerId = ?", (freelancerId,))
            connection.commit()
            return cursor.rowcount