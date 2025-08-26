from flask import (
    Blueprint, flash, redirect, render_template, 
    request, session, url_for
)
from handler import models, db
from .recruiter_auth import recruiter_login_required


recruiter_dashboard = Blueprint('recruiter_dashboard', __name__, url_prefix='/recruiter')

recruiterHandler = db.RecruiterHandler()
jobPostHandler = db.JobPostHandler()
jobSkillHandler = db.JobSkillHandler()
jobApplicationHandler = db.JobApplicationHandler()
userHandler = db.UserHandler()
resumeHandler = db.ResumeHandler()


@recruiter_dashboard.get('/')
@recruiter_login_required
def dashboard():
    recruiterId = session.get('recruiterId', "")
    
    # Get recruiter's jobs
    jobs = jobPostHandler.get_job_posts_by_recruiter(recruiterId)
    if jobs is None:
        jobs = []
    
    # Get job statistics
    total_jobs = len(jobs)
    total_applications = 0
    
    job_data = []
    for job in jobs:
        # Get skills for each job
        job_skills = jobSkillHandler.get_job_skills_with_names(job.jobId)
        skills = [{"skillId": skill.skillId, "skill": skill.skill} for skill in job_skills] if job_skills else []
        
        # Get application count
        applications = jobApplicationHandler.get_applications_by_job(job.jobId)
        application_count = len(applications) if applications else 0
        total_applications += application_count
        
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
    
    stats = {
        "totalJobs": total_jobs,
        "totalApplications": total_applications
    }
    
    return render_template('recruiter/dashboard.html', 
                         jobs=job_data, 
                         stats=stats,
                         recruiterName=session.get('recruiterName'))


@recruiter_dashboard.get('/profile')
@recruiter_login_required
def profile():
    recruiterId = session.get('recruiterId', "")
    recruiter = recruiterHandler.get_recruiter(recruiterId)
    
    if not recruiter:
        flash('Profile not found', 'error')
        return redirect(url_for('recruiter_dashboard.dashboard'))
    
    # Get recruiter's jobs for profile display
    jobs = jobPostHandler.get_job_posts_by_recruiter(recruiterId)
    if jobs is None:
        jobs = []
    
    # Calculate statistics
    total_jobs = len(jobs)
    total_applications = 0
    
    job_data = []
    for job in jobs:
        # Get skills for each job
        job_skills = jobSkillHandler.get_job_skills_with_names(job.jobId)
        skills = [{"skillId": skill.skillId, "skill": skill.skill} for skill in job_skills] if job_skills else []
        
        # Get application count
        applications = jobApplicationHandler.get_applications_by_job(job.jobId)
        application_count = len(applications) if applications else 0
        total_applications += application_count
        
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
    
    stats = {
        "totalJobs": total_jobs,
        "totalApplications": total_applications
    }
    
    return render_template('recruiter/profile.html', 
                         recruiter=recruiter, 
                         jobs=job_data, 
                         stats=stats)


@recruiter_dashboard.get('/jobs')
@recruiter_login_required
def jobs():
    recruiterId = session.get('recruiterId', "")
    
    # Get recruiter's jobs
    jobs = jobPostHandler.get_job_posts_by_recruiter(recruiterId)
    if jobs is None:
        jobs = []
    
    job_data = []
    for job in jobs:
        # Get skills for each job
        job_skills = jobSkillHandler.get_job_skills_with_names(job.jobId)
        skills = [{"skillId": skill.skillId, "skill": skill.skill} for skill in job_skills] if job_skills else []
        
        # Get application count
        applications = jobApplicationHandler.get_applications_by_job(job.jobId)
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
    
    return render_template('recruiter/jobs.html', jobs=job_data)


@recruiter_dashboard.get('/jobs/<int:job_id>')
@recruiter_login_required
def job_detail(job_id):
    recruiterId = session.get('recruiterId', "")
    
    # Get job details
    job = jobPostHandler.get_job_post(job_id)
    if not job or job.recruiterId != recruiterId:
        flash('Job not found or unauthorized', 'error')
        return redirect(url_for('recruiter_dashboard.jobs'))
    
    # Get job skills
    job_skills = jobSkillHandler.get_job_skills_with_names(job_id)
    skills = [{"skillId": skill.skillId, "skill": skill.skill} for skill in job_skills] if job_skills else []
    
    # Get applications for this job
    applications = jobApplicationHandler.get_applications_by_job(job_id)
    application_data = []
    
    if applications:
        for app in applications:
            freelancer = userHandler.get_user(app.freelancerId)
            freelancer_profile = userHandler.get_user_profile(app.freelancerId)
            
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
    
    job_data = {
        "jobId": job.jobId,
        "title": job.title,
        "description": job.description,
        "location": job.location,
        "salary": job.salary,
        "experience": job.experience,
        "skills": skills,
        "applications": application_data
    }
    
    return render_template('recruiter/job_detail.html', job=job_data)


@recruiter_dashboard.get('/jobs/create')
@recruiter_login_required
def create_job_form():
    return render_template('recruiter/create_job.html')


@recruiter_dashboard.post('/jobs/create')
@recruiter_login_required
def create_job_post():
    recruiterId = session.get('recruiterId', "")
    form = request.form
    
    title = form.get('title', '').strip()
    description = form.get('description', '').strip()
    location = form.get('location', '').strip()
    salary = form.get('salary', '0')
    experience = form.get('experience', '0')
    
    # Validate required fields
    if not title:
        flash('Job title is required', 'error')
        return redirect(url_for('recruiter_dashboard.create_job_form'))
    
    if not description:
        flash('Job description is required', 'error')
        return redirect(url_for('recruiter_dashboard.create_job_form'))
    
    # Convert salary and experience to appropriate types
    try:
        salary = float(salary) if salary else 0.0
        experience = int(experience) if experience else 0
    except ValueError:
        flash('Invalid salary or experience value', 'error')
        return redirect(url_for('recruiter_dashboard.create_job_form'))
    
    # Create job post
    job = models.JobPost(
        recruiterId=recruiterId,
        title=title,
        description=description,
        location=location,
        salary=salary,
        experience=experience
    )
    
    created_job = jobPostHandler.create_job_post(job)
    
    if not created_job:
        flash('Failed to create job post', 'error')
        return redirect(url_for('recruiter_dashboard.create_job_form'))
    
    flash('Job post created successfully! You can now add skills to your job.', 'success')
    return redirect(url_for('recruiter_dashboard.job_detail', job_id=created_job.jobId))


@recruiter_dashboard.get('/jobs/<int:job_id>/edit')
@recruiter_login_required
def edit_job_form(job_id):
    recruiterId = session.get('recruiterId', "")
    
    # Get job details
    job = jobPostHandler.get_job_post(job_id)
    if not job or job.recruiterId != recruiterId:
        flash('Job not found or unauthorized', 'error')
        return redirect(url_for('recruiter_dashboard.jobs'))
    
    # Get job skills
    job_skills = jobSkillHandler.get_job_skills_with_names(job_id)
    
    return render_template('recruiter/edit_job.html', 
                         job=job, 
                         job_skills=job_skills)


@recruiter_dashboard.post('/jobs/<int:job_id>/edit')
@recruiter_login_required
def edit_job_post(job_id):
    recruiterId = session.get('recruiterId', "")
    
    # Verify job ownership
    existing_job = jobPostHandler.get_job_post(job_id)
    if not existing_job or existing_job.recruiterId != recruiterId:
        flash('Job not found or unauthorized', 'error')
        return redirect(url_for('recruiter_dashboard.jobs'))
    
    form = request.form
    
    title = form.get('title', '').strip()
    description = form.get('description', '').strip()
    location = form.get('location', '').strip()
    salary = form.get('salary', '0')
    experience = form.get('experience', '0')
    
    # Validate required fields
    if not title:
        flash('Job title is required', 'error')
        return redirect(url_for('recruiter_dashboard.edit_job_form', job_id=job_id))
    
    if not description:
        flash('Job description is required', 'error')
        return redirect(url_for('recruiter_dashboard.edit_job_form', job_id=job_id))
    
    # Convert salary and experience to appropriate types
    try:
        salary = float(salary) if salary else 0.0
        experience = int(experience) if experience else 0
    except ValueError:
        flash('Invalid salary or experience value', 'error')
        return redirect(url_for('recruiter_dashboard.edit_job_form', job_id=job_id))
    
    # Update job post
    updated_job = models.JobPost(
        jobId=job_id,
        recruiterId=recruiterId,
        title=title,
        description=description,
        location=location,
        salary=salary,
        experience=experience
    )
    
    result = jobPostHandler.update_job_post(updated_job)
    
    if not result:
        flash('Failed to update job post', 'error')
        return redirect(url_for('recruiter_dashboard.edit_job_form', job_id=job_id))
    
    flash('Job post updated successfully!', 'success')
    return redirect(url_for('recruiter_dashboard.job_detail', job_id=job_id))


@recruiter_dashboard.post('/jobs/<int:job_id>/delete')
@recruiter_login_required
def delete_job_post(job_id):
    recruiterId = session.get('recruiterId', "")
    
    # Verify job ownership
    existing_job = jobPostHandler.get_job_post(job_id)
    if not existing_job or existing_job.recruiterId != recruiterId:
        flash('Job not found or unauthorized', 'error')
        return redirect(url_for('recruiter_dashboard.jobs'))
    
    # Delete the job post (this will cascade delete skills and applications)
    success = jobPostHandler.delete_job_post(job_id)
    
    if success:
        flash('Job post deleted successfully', 'success')
    else:
        flash('Failed to delete job post', 'error')
    
    return redirect(url_for('recruiter_dashboard.jobs'))


@recruiter_dashboard.get('/applications')
@recruiter_login_required
def all_applications():
    recruiterId = session.get('recruiterId', "")
    
    # Get all jobs by this recruiter
    jobs = jobPostHandler.get_job_posts_by_recruiter(recruiterId)
    if not jobs:
        return render_template('recruiter/applications.html', applications=[])
    
    all_applications = []
    
    for job in jobs:
        applications = jobApplicationHandler.get_applications_by_job(job.jobId)
        if applications:
            for app in applications:
                freelancer = userHandler.get_user(app.freelancerId)
                freelancer_profile = userHandler.get_user_profile(app.freelancerId)
                
                if freelancer:
                    app_data = {
                        "jobId": app.jobId,
                        "jobTitle": job.title,
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
                    
                    all_applications.append(app_data)
    
    return render_template('recruiter/applications.html', applications=all_applications)


@recruiter_dashboard.get('/resume/<int:resume_id>')
@recruiter_login_required
def view_resume(resume_id):
    from flask import Response
    
    resume = resumeHandler.get_resume(resume_id)
    
    if not resume:
        flash('Resume not found', 'error')
        return redirect(url_for('recruiter_dashboard.all_applications'))
    
    # Return PDF as response
    return Response(
        resume.pdfData,
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'inline; filename="{resume.name}.pdf"',
            'Content-Type': 'application/pdf'
        }
    )