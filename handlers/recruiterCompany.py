from .db import DB
from models import RecruiterCompany

class RecruiterCompanyHandler:
    def __init__(self):
        self.db = DB()
    
    def create(self, recruiterCompany: RecruiterCompany):
        with self.db as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("INSERT INTO recruiterCompanies (recruiterId, companyId, role) VALUES (?, ?, ?)", (recruiterCompany.recruiterId, recruiterCompany.companyId, recruiterCompany.role))
            connection.commit()
            return True
    
    def remove(self, recruiterId, companyId):
        with self.db as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("DELETE FROM recruiterCompanies WHERE recruiterId = ? AND companyId = ?", (recruiterId, companyId))
            connection.commit()
            return True
    
    def exists(self, recruiterId, companyId):
        with self.db as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM recruiterCompanies WHERE recruiterId = ? AND companyId = ?", (recruiterId, companyId))
            res = cursor.fetchone()
            return res is not None
    
    def get_by_recruiter(self, recruiterId):
        with self.db as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM recruiterCompanies WHERE recruiterId = ?", (recruiterId,))
            res = cursor.fetchall()
            return [RecruiterCompany(recruiterId=row[1], companyId=row[2]) for row in res]
    
    def get_by_company(self, companyId):
        with self.db as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM recruiterCompanies WHERE companyId = ?", (companyId,))
            res = cursor.fetchall()
            return [RecruiterCompany(recruiterId=row[1], companyId=row[2]) for row in res]
    
    def update(self, recruiterCompany: RecruiterCompany):
        with self.db as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("UPDATE recruiterCompanies SET role = ? WHERE recruiterId = ? AND companyId = ?", (recruiterCompany.role, recruiterCompany.recruiterId, recruiterCompany.companyId))
            connection.commit()
            return True