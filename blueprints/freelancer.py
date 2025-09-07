from flask import (
    Blueprint, request, jsonify, abort, send_file,
    current_app as app, redirect, flash, get_flashed_messages,
    url_for, session, render_template
)
from flask_jwt_extended import (
    create_access_token, 
    set_access_cookies, 
    unset_jwt_cookies,
    jwt_required, 
    get_jwt_identity
)
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError
from hashlib import sha256
from db import models


freelancer = Blueprint("freelancer", __name__)


@freelancer.errorhandler(NoAuthorizationError)
def handle_auth_errors(e):
    return redirect(url_for('freelancer.login'))

@freelancer.errorhandler(InvalidHeaderError)
def handle_invalid_header_errors(e):
    return redirect(url_for('freelancer.login'))



@freelancer.get("/")
@jwt_required()
def index():
    # get current user
    cookie = get_jwt_identity()
    if not cookie:
        print("no cookie")
        return redirect(url_for("freelancer.login"))
    
    fid = int(cookie.split(',')[0])
    
    if cookie.split(',')[-1] != "freelancer":
        return redirect(url_for("freelancer.login"))
    
    freelancer = models.Freelancers.get(id=fid)
    
    if not freelancer:
        print("no get freelancer")
        return redirect(url_for("freelancer.login"))
    
    freelancerDetail = models.FreelancerDetails.get(freelancerId=fid)
    educations = models.Educations.getAll(freelancerId=fid)
    experiences = models.Experiences.getAll(freelancerId=fid)
    rawSkills = models.FreelancerSkills.getAll(freelancerId=fid)
    skills = []
    
    for skill in rawSkills:
        skills.append({"skill": models.Skills.get(id=skill["skillId"]), "proficiencyLevel": skill["proficiencyLevel"], "yearsOfExperience": skill["yearsOfExperience"]})
    
    return render_template(
        "/freelancer/index.html", freelancer=freelancer, 
        freelancerDetails=freelancerDetail, 
        educations=educations, experiences=experiences, 
        skills=skills
    )


@freelancer.get("/login")
def login():
    return render_template("/freelancer/login.html")


@freelancer.get("/signup")
def signup():
    return render_template("/freelancer/signup.html")

@freelancer.get("/profile")
@jwt_required()
def profile():
    return render_template("/freelancer/profile.html")


@freelancer.get("/jobs")
@jwt_required()
def jobs():
    # Get search parameters from request args
    search = request.args.get("search", "")
    page = int(request.args.get("page", 0))
    
    # Get filter parameters
    min_experience = request.args.get("min_experience")
    max_experience = request.args.get("max_experience")
    job_type = request.args.get("job_type")
    company_name = request.args.get("company_name")
    min_salary = request.args.get("min_salary")
    max_salary = request.args.get("max_salary")
    skills = request.args.get("skills")
    location = request.args.get("location")
    applied = bool(request.args.get("applied", 0))
    
    # Convert string parameters to appropriate types
    min_experience = int(min_experience) if min_experience and min_experience.isdigit() else None
    max_experience = int(max_experience) if max_experience and max_experience.isdigit() else None
    min_salary = float(min_salary) if min_salary and min_salary.replace('.', '').isdigit() else None
    max_salary = float(max_salary) if max_salary and max_salary.replace('.', '').isdigit() else None
    
    # Perform search with all filters
    jobs = models.JobPosts.search(
        search=search,
        page=page,
        min_experience=min_experience,
        max_experience=max_experience,
        job_type=job_type,
        company_name=company_name,
        min_salary=min_salary,
        max_salary=max_salary,
        skills=skills,
        location=location
    )
    
    applicationModels = models.Applications.getAll(freelancerId = get_jwt_identity().split(',')[0])
    applicationIds = [ i.jobPostId for i in applicationModels ]
    
    print(jobs)
    if applied:
        jobs = [job for job in jobs if job.id in applicationIds]
    else:
        jobs = [job for job in jobs if job['id'] not in applicationIds]
    
    return render_template("/freelancer/jobs.html", jobs=jobs)



@freelancer.get("/apply/<int:jobId>")
@jwt_required()
def apply_job(jobId):
    cookie = get_jwt_identity()
    current_user_id = int(cookie.split(',')[0])
    
    if not cookie:
        print("no cookie")
        return redirect(url_for("freelancer.login"))
    
    if cookie.split(',')[-1] != "freelancer":
        return redirect(url_for("freelancer.login"))

        # Check if user has already applied
    existing_application = models.Applications.get(jobPostId=jobId, freelancerId=current_user_id)
    if existing_application:
        return redirect(url_for('freelancer.application_status', jobId=jobId))
    
    # Get job details with company and skills
    job = models.JobPosts.get(id=jobId)
    if not job:
        flash("Job not found", "error")
        return redirect(url_for('freelancer.jobs'))
    
    # Get company details
    company = models.Companies.get(id=job.companyId)
    if not company:
        flash("Company information not found", "error")
        return redirect(url_for('freelancer.jobs'))
    
    # Get user's existing resumes
    user_resumes = models.Resumes.getAll(freelancerId=current_user_id)
    
    return render_template("/freelancer/apply.html", 
                            job=job, 
                            company=company, 
                            resumes=user_resumes,
                            freelancer=models.Freelancers.get(id=current_user_id)
                            )
@freelancer.post("/apply/<int:jobId>")
def apply_post(jobId): 
    print(request.form)
    freelancerId = request.form.get('freelancerId', None)
    
    if not freelancerId:
        print("no freelancerId")
        return redirect(url_for("freelancer.login"))
    
    current_user_id = int(freelancerId)
    
    if not current_user_id:
        print("no current_user_id")
        return redirect(url_for("freelancer.login"))

    
    # Check if user has already applied (double-check)
    existing_application = models.Applications.get(jobPostId=jobId, freelancerId=current_user_id)
    if existing_application:
        flash("You have already applied for this job", "warning")
        return redirect(url_for('freelancer.application_status', jobId=jobId))
    
    # Get form data
    cover_letter = request.form.get('cover_letter')
    resume_choice = request.form.get('resume_choice')  # 'existing' or 'new'
    resume_id = None
    
    print(resume_choice)
    print(resume_id)
    
    if resume_choice == 'existing':
        resume_id = request.form.get('existing_resume_id')
        if not resume_id:
            flash("Please select an existing resume", "error")
            return redirect(url_for('freelancer.apply_job', jobId=jobId))
        resume_id = int(resume_id)
    
    elif resume_choice == 'new':
        # Handle new resume upload
        if 'resume_file' not in request.files:
            flash("Please upload a resume file", "error")
            return redirect(url_for('freelancer.apply_job', jobId=jobId))
        
        resume_file = request.files['resume_file']
        resume_name = request.form.get('resume_name', '')
        
        if not resume_file:
            flash("Please upload a resume file", "error")
            return redirect(url_for('freelancer.apply_job', jobId=jobId))
        
        if resume_file.filename == '':
            flash("Please select a resume file", "error")
            return redirect(url_for('freelancer.apply_job', jobId=jobId))
        
        if not resume_name:
            resume_name = resume_file.filename
        
        if not resume_name:
            flash("Please provide a resume name", "error")
            return redirect(url_for('freelancer.apply_job', jobId=jobId))
        
        # Read file data
        resume_data = resume_file.read()
        file_size = len(resume_data)
        
        # Create new resume record
        new_resume = models.Resumes(
            freelancerId=current_user_id,
            name=resume_name,
            pdfData=resume_data,
            fileSize=file_size,
            isDefault=False
        )
        
        resume_id = new_resume.insert()
        if not resume_id:
            flash("Failed to upload resume", "error")
            return redirect(url_for('freelancer.apply_job', jobId=jobId))
    
    else:
        flash("Please select a resume option", "error")
        return redirect(url_for('freelancer.apply_job', jobId=jobId))
    
    # Create application
    application = models.Applications(
        jobPostId=jobId,
        freelancerId=current_user_id,
        resumeId=resume_id,
        coverLetter=cover_letter,
        status="PENDING"
    )
    
    application_id = application.insert()
    if application_id:
        flash("Application submitted successfully!", "success")
        return redirect(url_for('freelancer.application_status', jobId=jobId))
    else:
        flash("Failed to submit application", "error")
        return redirect(url_for('freelancer.apply_job', jobId=jobId))


@freelancer.route("/application/<int:jobId>")
@jwt_required()
def application_status(jobId):
    cookie = get_jwt_identity()
    current_user_id = int(cookie.split(',')[0])

    if not cookie:
        print("no cookie")
        return redirect(url_for("freelancer.login"))
    
    if cookie.split(',')[-1] != "freelancer":
        return redirect(url_for("freelancer.login"))

    # Get application details
    application = models.Applications.get(jobPostId=jobId, freelancerId=current_user_id)
    if not application:
        flash("Application not found", "error")
        return redirect(url_for('freelancer.jobs'))
    
    # Get job details with company and skills
    job = models.JobPosts.get(id=jobId)
    if not job:
        flash("Job not found", "error")
        return redirect(url_for('freelancer.jobs'))
    
    # Get company details
    company = models.Companies.get(id=job.companyId)
    
    # Get resume details
    resume = models.Resumes.get(id=application.resumeId)
    
    return render_template("/freelancer/application_status.html", 
                         application=application,
                         job=job, 
                         company=company,
                         resume=resume)


@freelancer.route("applications")
@jwt_required()
def applications():
    cookie = get_jwt_identity()
    current_user_id = int(cookie.split(',')[0])

    if not cookie:
        print("no cookie")
        return redirect(url_for("freelancer.login"))
    
    if cookie.split(',')[-1] != "freelancer":
        return redirect(url_for("freelancer.login"))

    # Get all applications for the current user
    user_applications = models.Applications.getAll(freelancerId=current_user_id)
    
    if not user_applications:
        return render_template("/freelancer/applications.html", applications=[])
    
    # Enhance applications with job, company, and resume details
    enhanced_applications = []
    
    for application in user_applications:
        # Get job details
        job = models.JobPosts.get(id=application.jobPostId)
        if not job:
            continue
            
        # Get company details
        company = models.Companies.get(id=job.companyId)
        
        # Get resume details
        resume = models.Resumes.get(id=application.resumeId)
        
        # Create enhanced application object
        enhanced_app = {
            'application': application,
            'job': job,
            'company': company,
            'resume': resume
        }
        
        enhanced_applications.append(enhanced_app)
    
    # Sort by application date (most recent first)
    enhanced_applications.sort(key=lambda x: x['application'].appliedOn or '0000-00-00', reverse=True)
    
    return render_template("/freelancer/applications.html", applications=enhanced_applications)
