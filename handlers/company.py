from .db import DB
from models import Company


class CompanyHandler:
    def get(self, companyId):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM companies WHERE companyId = ?", (companyId,))
            row = cursor.fetchone()

            if row is None:
                return None

            return Company(
                id = row[0],
                username = row[1],
                companyName = row[2],
                companyPhone = row[3],
                companyAddress = row[4],
                companyDescription = row[5],
                employeeSize = row[6]
            )
    
    def get_all_companies(self):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM companies")
            rows = cursor.fetchall()
            return [Company(
                id = row[0],
                username = row[1],
                companyName = row[2],
                companyPhone = row[3],
                companyAddress = row[4],
                companyDescription = row[5],
                employeeSize = row[6]
            ) for row in rows]
    
    def create(self, company: Company):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO companies (username, companyName, companyPhone, companyAddress, companyDescription, employeeSize) VALUES (?, ?, ?, ?, ?, ?)",
                (company.username, company.companyName, company.companyPhone, company.companyAddress, company.companyDescription, company.employeeSize)
            )
            connection.commit()
            return cursor.lastrowid
    
    def get_with_username(self, username):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM companies WHERE username = ?", (username,))
            row = cursor.fetchone()

            if row is None:
                return None

            return Company(
                id = row[0],
                username = row[1],
                companyName = row[2],
                companyPhone = row[3],
                companyAddress = row[4],
                companyDescription = row[5],
                employeeSize = row[6]
            )

    def remove(self, companyId):
        with DB() as connection:
            if not connection:
                return None
            cursor = connection.cursor()
            cursor.execute("DELETE FROM companies WHERE companyId = ?", (companyId,))
            connection.commit()
            return True