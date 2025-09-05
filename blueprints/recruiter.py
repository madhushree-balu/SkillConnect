from functools import wraps
from flask import (
    Blueprint, request,
    redirect, flash,
    url_for, render_template
)
from flask_jwt_extended import (
    jwt_required, 
    get_jwt_identity
)
from db import models


recruiter = Blueprint("recruiter", __name__)


def login_required(f):
    # Since most of the functions use the same cookie verification logic,
    # this wrapper is created to avoid code duplication
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        # load the cookie from the request
        cookie = get_jwt_identity()
        if not cookie:
            print("no cookie")
            flash("You need to login first!", "warning")
            return redirect(url_for("recruiter.login"))
        
        try:
            # the cookie will be in the form of "id,role"
            parts = cookie.split(',')
            if len(parts) < 2 or parts[-1] != "recruiter":
                flash("You need to login first!", "warning")
                return redirect(url_for("recruiter.login"))
            
            recruiter = models.Recruiters.get(id=int(parts[0]))
        except (ValueError, IndexError):
            flash("Invalid session", "warning")
            return redirect(url_for("recruiter.login"))
        
        if not recruiter:
            print("no recruiter")
            flash("You need to login first!", "warning")
            return redirect(url_for("recruiter.login"))
        
        return f(recruiter, *args, **kwargs)
    return decorated_function


@recruiter.get("/")
@login_required
def index(recruiter):
    # get all the companies that the recruiter is associated with
    recruiterCompanies = models.RecruiterCompanies.getAll(recruiterId=recruiter.id)
    companies = {}
    
    # get all the company details
    for i in recruiterCompanies:
        company = models.Companies.get(id=i.companyId)
        if company:  # Add this check
            companies[company.id] = company.model_dump()
    
    # get all the job posts
    posts = models.JobPosts.getAll(recruiterId=recruiter.id)
    
    companyPosts = {}
    
    for post in posts:
        if post.companyId in companyPosts:
            companyPosts[post.companyId].append(post)
        else:
            companyPosts[post.companyId] = [post]
    
    return render_template("/recruiter/index.html", recruiter=recruiter, companies=companies, companyPosts=companyPosts)


@recruiter.get("/login")
def login():
    return render_template("/recruiter/login.html")


@recruiter.get("/signup")
def signup():
    return render_template("/recruiter/signup.html")


@recruiter.get("/profile")
@login_required
def profile(recruiter):
    return render_template("/recruiter/profile.html", recruiter=recruiter)


@recruiter.get("/company/create")
@login_required
def create_company(recruiter):
    return render_template("/recruiter/create_company.html", recruiter=recruiter)


@recruiter.get("/company/<id>")
@login_required
def company(recruiter, id):
    # check if the recruiter is associated with the company
    rc = models.RecruiterCompanies.get(recruiterId=recruiter.id, companyId=id)
    if not rc:
        flash("Company not found", "error")
        return redirect(url_for("recruiter.index"))
    
    # get the company details
    companyModel = models.Companies.get(id=id)
    if not companyModel:
        flash("Company not found", "error")
        return redirect(url_for("recruiter.index"))
    
    # get the recruiters associated with the company
    companyRecruiters = models.RecruiterCompanies.getAll(companyId=id)
    
    # get the recruiter details with the roles
    recruiters = {}
    for i in companyRecruiters:
        recruiter_obj = models.Recruiters.get(id=i.recruiterId)
        if recruiter_obj:
            recruiter_data = recruiter_obj.model_dump()
            recruiter_data["role"] = i.role
            recruiters[recruiter_obj.id] = recruiter_data
    
    return render_template("/recruiter/company.html", recruiter=recruiter, rc=rc , company=companyModel, recruiters = recruiters)


@recruiter.get("/post/create")
@login_required
def create_post(recruiter):
    # get all the companies that the recruiter is associated with
    recruiterCompanies = models.RecruiterCompanies.getAll(recruiterId=recruiter.id)
    companies = []

    for i in recruiterCompanies:
        company = models.Companies.get(id=i.companyId)
        if company:  # Add this check
            companies.append(company)
    
    return render_template("/recruiter/create_post.html", companies=companies)


@recruiter.get("/post/<id>")
@login_required
def post(recruiter, id):
    # get the post from the database
    post = models.JobPosts.get(id=id)
    if not post:
        flash("Post not found", "error")
        return redirect(url_for("recruiter.index"))
    
    # check if the recruiter is associated with the company
    isInCompany = models.RecruiterCompanies.get(recruiterId = recruiter.id, companyId=post.companyId)
    if not isInCompany:
        flash("You don't have access to this post", "error")
        return redirect(url_for("recruiter.index"))
    
    # get the skills associated with the post
    skills = []
    for post_skill in models.PostSkills.getAll(postId=id):
        skill = models.Skills.get(id=post_skill.skillId)
        if skill is None:
            continue
        skills.append(skill.model_dump())
        
    # get the applications
    applicationModels = models.Applications.getAll(jobPostId=id)
    applications = []
    for i in applicationModels:
        freelancer = models.Freelancers.get(id=i.freelancerId)
        if freelancer:
            i = i.model_dump()
            i['freelancer'] = freelancer.model_dump()
            applications.append(i)
    
    return render_template("/recruiter/post.html",recruiter=recruiter , post=post, skills=skills, applications=applications)

