from .db import DB
from models import FreelancerDetails

class FreelancerDetailsHandler:
    def __init__(self):
        self.db = DB()
    
    def create(self, freelancer_details: FreelancerDetails):
        with self.db as conn:
            conn.execute("INSERT INTO freelancer_details VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
                freelancer_details.freelancerId,
                freelancer_details.firstName,
                freelancer_details.middleName,
                freelancer_details.lastName,
                freelancer_details.phoneNumber,
                freelancer_details.contactEmail,
                freelancer_details.about,
                freelancer_details.dateOfBirth
            ))
            conn.commit()

        return freelancer_details

    def update_freelancer_details(self, freelancer_details: FreelancerDetails):
        with self.db as conn:
            conn.execute("UPDATE freelancer_details SET firstName = ?, middleName = ?, lastName = ?, phoneNumber = ?, contactEmail = ?, about = ?, dateOfBirth = ? WHERE freelancerId = ?", (
                freelancer_details.firstName,
                freelancer_details.middleName,
                freelancer_details.lastName,
                freelancer_details.phoneNumber,
                freelancer_details.contactEmail,
                freelancer_details.about,
                freelancer_details.dateOfBirth,
                freelancer_details.freelancerId
            ))
            conn.commit()

        return freelancer_details

    def delete_freelancer_details(self, freelancerId):
        with self.db as conn:
            conn.execute("DELETE FROM freelancer_details WHERE freelancerId = ?", (freelancerId,))
            conn.commit()
        return True

    def get_freelancer_details(self, freelancerId):
        with self.db as conn:
            res = conn.execute("SELECT * FROM freelancer_details WHERE freelancerId = ?", (freelancerId,))
            row = res.fetchone()

            if row is None:
                return None

            return FreelancerDetails(
                freelancerId=row[0],
                firstName=row[1],
                middleName=row[2],
                lastName=row[3],
                phoneNumber=row[4],
                contactEmail=row[5],
                about=row[6],
                dateOfBirth=row[7]
            )