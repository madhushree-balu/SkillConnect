import handlers
import models
import datetime

class Wrapper:
    def __init__(self):
        self.application = handlers.ApplicationHandler()
        self.experience = handlers.ExperienceHandler()
        self.freelancerSkill = handlers.FreelancerSkillHandler()
        self.freelancerDetails = handlers.FreelancerDetailsHandler()
        self.education = handlers.EducationHandler()
        self.jobPost = handlers.JobPostHandler()
        self.company = handlers.CompanyHandler()
        self.skill = handlers.SkillHandler()
        self.recruiter = handlers.RecruiterHandler()
        self.postSkill = handlers.PostSkillHandler()
        self.freelancer = handlers.FreelancerHandler()
        self.recruiterCompanyPost = handlers.RecruiterCompanyPostHandler()
        self.recruiterCompany = handlers.RecruiterCompanyHandler()
    
    def create_freelancer(self, freelancer: models.Freelancer):
        freelancerId = self.freelancer.create(freelancer)
        
        if freelancerId is None:
            return None
        
        # initiate personal details
        freelancerDetail = models.FreelancerDetails(freelancerId=freelancerId, firstName=freelancer.username, middleName="", lastName=freelancer.email, phoneNumber="", contactEmail="", about="", dateOfBirth="")
        self.freelancerDetails.create(freelancerDetail)

        return freelancerId
    
    
    def create_company(self, recruiter: models.Recruiter, company: models.Company):
        companyId = self.company.create(company)
        if not companyId:
            return None
        recruiterCompany = models.RecruiterCompany(recruiterId=recruiter.id, companyId=companyId, role="ADMIN")
        self.recruiterCompany.create(recruiterCompany)
        return companyId

    def join_company(self, recruiter: models.Recruiter, companyId: int, role="RECRUITER"):
        if not self.recruiterCompany.exists(recruiter.id, companyId):
            return None
        recruiterCompany = models.RecruiterCompany(recruiterId=recruiter.id, companyId=companyId, role=role)
        return self.recruiterCompany.create(recruiterCompany)
    
    def make_company_admin(self, recruiter: models.Recruiter, companyId: int):
        if not self.recruiterCompany.exists(recruiter.id, companyId):
            return None
        recruiterCompany = models.RecruiterCompany(recruiterId=recruiter.id, companyId=companyId, role="ADMIN")
        return self.recruiterCompany.update(recruiterCompany)

    def remove_recruiter_from_company(self, recruiter: models.Recruiter, companyId: int):
        if not self.recruiterCompany.exists(recruiter.id, companyId):
            return None
        return self.recruiterCompany.remove(recruiter.id, companyId)
   
    def create_job_post(self, recruiter: models.Recruiter, company: models.Company, jobPost: models.JobPost, postedOn, validTill):
        postId = self.jobPost.create(jobPost)
        
        if not postId:
            return None
        
        recruiterCompanyPost = models.RecruiterCompanyPost(recruiterId=recruiter.id, companyId=company.id, postId=postId, postedOn=postedOn, validTill=validTill) 
        self.recruiterCompanyPost.create(recruiterCompanyPost)
        
        return postId

    def add_skill_to_post(self, postId: int, skill: str):
        skillId = self.skill.get_or_create_skill(skill)
        if not skillId:
            return None
        postSkill = models.PostSkill(postId=postId, skillId=skillId)
        res = self.postSkill.create(postSkill)
    
        return postSkill if res else None