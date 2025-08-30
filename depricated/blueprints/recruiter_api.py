from flask import (
    Blueprint, flash, redirect, render_template, 
    request, session, url_for
)
from handler import models, db


recruiter_api = Blueprint('recruiter_api', __name__, url_prefix='/recruiter/api')


@recruiter_api.get("/")
def index():
    return {
        "success": True
    }


@recruiter_api.post("/profile/modify")
def modify_recruiter_profile():
    recruiterId = session.get("recruiterId")
    
    if recruiterId is None:
        return {
            "success": False,
            "error": "Recruiter is not logged in!"
        }
    
    data = request.get_json()
    
    # Get current recruiter data first
    current_recruiter = db.RecruiterHandler().get_recruiter(recruiterId)
    if not current_recruiter:
        return {
            "success": False,
            "error": "Recruiter not found!"
        }
    
    updatedRecruiter = models.Recruiter(
        recruiterId=recruiterId,
        name=data.get("name", current_recruiter.name),
        email=data.get("email", current_recruiter.email),
        password=current_recruiter.password,  # Keep existing password
        company=data.get("company", current_recruiter.company),
        location=data.get("location", current_recruiter.location),
        website=data.get("website", current_recruiter.website),
        contact_email=data.get("contact_email", current_recruiter.contact_email),
        contact_number=data.get("contact_number", current_recruiter.contact_number)
    )
    
    updatedRecruiterProfile = db.RecruiterHandler().update_recruiter(updatedRecruiter)
    
    if updatedRecruiterProfile:
        return {
            "success": True
        }
    
    return {
        "success": False,
        "error": "Could not update profile!"
    }


@recruiter_api.post("/jobs/create")
def create_job():
    recruiterId = session.get("recruiterId")
    
    if recruiterId is None:
        return {
            "success": False,
            "error": "Recruiter is not logged in!"
        }
    
    emptyJob = models.JobPost(
        recruiterId=recruiterId,
        title="New Job Post",
        description="Job description"
    )

    job = db.JobPostHandler().create_job_post(emptyJob)

    if job:
        return {
            "success": True,
            "jobId": job.jobId
        }

    return {
        "success": False,
        "error": "Could not create new job post!"
    }


@recruiter_api.post("/jobs/modify")
def modify_job():
    recruiterId = session.get("recruiterId")
    data = request.get_json()

    if recruiterId is None:
        return {
            "success": False,
            "error": "Recruiter is not logged in!"
        }

    # Verify job belongs to this recruiter
    existing_job = db.JobPostHandler().get_job_post(data["jobId"])
    if not existing_job or existing_job.recruiterId != recruiterId:
        return {
            "success": False,
            "error": "Job not found or unauthorized!"
        }

    updatedJob = models.JobPost(
        jobId=data["jobId"],
        recruiterId=recruiterId,
        title=data["title"],
        description=data["description"],
        location=data.get("location", ""),
        salary=float(data.get("salary", 0.0)),
        experience=int(data.get("experience", 0))
    )

    job = db.JobPostHandler().update_job_post(updatedJob)
    
    if job:
        return {
            "success": True
        }

    return {
        "success": False,
        "error": "Could not update job post!"
    }


@recruiter_api.post("/jobs/remove")
def remove_job():
    recruiterId = session.get("recruiterId")
    form = request.get_json(force=True)
    jobId = form.get("jobId")
    
    if recruiterId is None:
        return {
            "success": False,
            "error": "Recruiter is not logged in!"
        }
    
    if jobId is None:
        return {
            "success": False,
            "error": "Job ID is required"
        }

    # Verify job belongs to this recruiter
    existing_job = db.JobPostHandler().get_job_post(jobId)
    if not existing_job or existing_job.recruiterId != recruiterId:
        return {
            "success": False,
            "error": "Job not found or unauthorized!"
        }
    
    return {
        "success": db.JobPostHandler().delete_job_post(jobId)
    }


@recruiter_api.post("/jobs/skills/add")
def add_job_skill():
    recruiterId = session.get("recruiterId")
    form = request.get_json(force=True)
    jobId = form.get("jobId")
    skill = form.get("skill")
    
    if recruiterId is None:
        return {
            "success": False,
            "error": "Recruiter is not logged in!"
        }
    
    if skill is None or skill == "":
        return {
            "success": False,
            "error": "Skill is required"
        }

    if jobId is None:
        return {
            "success": False,
            "error": "Job ID is required"
        }

    # Verify job belongs to this recruiter
    existing_job = db.JobPostHandler().get_job_post(jobId)
    if not existing_job or existing_job.recruiterId != recruiterId:
        return {
            "success": False,
            "error": "Job not found or unauthorized!"
        }

    jobSkill = db.JobSkillHandler().add_job_skill(jobId, skill)
    
    if jobSkill is None:
        return {
            "success": False,
            "error": "Skill already exists for this job"
        }
    
    return {
        "success": True,
        "skillId": jobSkill.skillId,
        "skill": skill
    }


@recruiter_api.post("/jobs/skills/remove")
def remove_job_skill():
    recruiterId = session.get("recruiterId")
    form = request.get_json(force=True)
    jobId = form.get("jobId")
    skillId = form.get("skillId")
    
    if recruiterId is None:
        return {
            "success": False,
            "error": "Recruiter is not logged in!"
        }
    
    if skillId is None:
        return {
            "success": False,
            "error": "Skill ID is required"
        }

    if jobId is None:
        return {
            "success": False,
            "error": "Job ID is required"
        }

    # Verify job belongs to this recruiter
    existing_job = db.JobPostHandler().get_job_post(jobId)
    if not existing_job or existing_job.recruiterId != recruiterId:
        return {
            "success": False,
            "error": "Job not found or unauthorized!"
        }
    
    return {
        "success": db.JobSkillHandler().remove_job_skill(jobId, skillId)
    }


@recruiter_api.get("/jobs/<int:job_id>/applications")
def get_job_applications(job_id):
    recruiterId = session.get("recruiterId")
    
    if recruiterId is None:
        return {
            "success": False,
            "error": "Recruiter is not logged in!"
        }

    # Verify job belongs to this recruiter
    existing_job = db.JobPostHandler().get_job_post(job_id)
    if not existing_job or existing_job.recruiterId != recruiterId:
        return {
            "success": False,
            "error": "Job not found or unauthorized!"
        }

    applications = db.JobApplicationHandler().get_applications_by_job(job_id)
    
    if applications is None:
        return {
            "success": False,
            "error": "Could not retrieve applications"
        }

    # Get freelancer details for each application
    application_data = []
    for app in applications:
        freelancer = db.UserHandler().get_user(app.freelancerId)
        freelancer_profile = db.UserHandler().get_user_profile(app.freelancerId)
        
        if freelancer:
            app_data = {
                "jobId": app.jobId,
                "freelancerId": app.freelancerId,
                "applicationDate": app.applicationDate,
                "resumeId": app.resumeId,
                "freelancer": {
                    "username": freelancer.username,
                    "email": freelancer.email
                }
            }
            
            if freelancer_profile:
                app_data["freelancer"].update({
                    "firstName": freelancer_profile.firstName,
                    "lastName": freelancer_profile.lastName,
                    "summary": freelancer_profile.summary,
                    "phoneNumber": freelancer_profile.phoneNumber,
                    "contactEmail": freelancer_profile.contactEmail
                })
            
            application_data.append(app_data)

    return {
        "success": True,
        "applications": application_data
    }


@recruiter_api.get("/resumes/<int:resume_id>")
def get_resume(resume_id):
    recruiterId = session.get("recruiterId")
    
    if recruiterId is None:
        return {
            "success": False,
            "error": "Recruiter is not logged in!"
        }

    resume = db.ResumeHandler().get_resume(resume_id)
    
    if not resume:
        return {
            "success": False,
            "error": "Resume not found!"
        }

    # Note: This returns resume metadata only
    # For actual PDF download, you'd need a separate endpoint
    return {
        "success": True,
        "resume": {
            "resumeId": resume.resumeId,
            "freelancerId": resume.freelancerId,
            "name": resume.name
        }
    }


@recruiter_api.get("/jobs")
def get_recruiter_jobs():
    recruiterId = session.get("recruiterId")
    
    if recruiterId is None:
        return {
            "success": False,
            "error": "Recruiter is not logged in!"
        }

    jobs = db.JobPostHandler().get_job_posts_by_recruiter(recruiterId)
    
    if jobs is None:
        return {
            "success": False,
            "error": "Could not retrieve jobs"
        }

    job_data = []
    for job in jobs:
        # Get skills for each job
        job_skills = db.JobSkillHandler().get_job_skills_with_names(job.jobId)
        skills = [{"skillId": skill.skillId, "skill": skill.skill} for skill in job_skills] if job_skills else []
        
        # Get application count
        applications = db.JobApplicationHandler().get_applications_by_job(job.jobId)
        application_count = len(applications) if applications else 0
        
        job_data.append({
            "jobId": job.jobId,
            "title": job.title,
            "description": job.description,
            "location": job.location,
            "salary": job.salary,
            "experience": job.experience,
            "skills": skills,
            "applicationCount": application_count
        })

    return {
        "success": True,
        "jobs": job_data
    }