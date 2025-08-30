from .db import DB
from models import Education

class EducationHandler:
    def create(self, education: Education):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            
            cursor.execute(
                "INSERT INTO education (freelancerId, school, degree, course, startDate, endDate, cgpa) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (education.freelancerId, education.school, education.degree, education.course, education.startDate, education.endDate, education.cgpa)
            )
            newEducationId = cursor.lastrowid
            connection.commit()
            return newEducationId
    
    def get_educations(self, freelancerId: int):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM education WHERE freelancerId = ?",
                (freelancerId,)
            )
            rows = cursor.fetchall()
            return [Education(
                id=row[0],
                freelancerId=row[1],
                school=row[2],
                degree=row[3],
                course=row[4],
                startDate=row[5],
                endDate=row[6],
                cgpa=row[7]
            ) for row in rows]
        
    def update_education(self, education: Education):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE education SET freelancerId = ?, school = ?, degree = ?, course = ?, startDate = ?, endDate = ?, cgpa = ? WHERE id = ?",
                (education.freelancerId, education.school, education.degree, education.course, education.startDate, education.endDate, education.cgpa, education.id)
            )
            connection.commit()
            return True