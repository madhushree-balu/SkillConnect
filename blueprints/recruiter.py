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
from hashlib import sha256
from db import models


recruiter = Blueprint("recruiter", __name__)


@recruiter.get("/")
@jwt_required()
def index():
    # get current user
    cookie = get_jwt_identity()
    if not cookie:
        print("no cookie")
        return jsonify({"error": "Unauthorized"}), 401
    
    if cookie.split(',')[-1] != "recruiter":
        print("no recruiter")
        return jsonify({"error": "Unauthorized"}), 401
    
    recruiter = models.Recruiters.get(id=int(cookie.split(',')[0]))
    
    print(cookie)
    if not recruiter:
        print("no get recruiter")
        return jsonify({"error": "Unauthorized"}), 401
    
    recruiterCompanies = models.RecruiterCompanies.getAll(recruiterId=recruiter.id)
    companies = []
    
    for i in recruiterCompanies:
        company = models.Companies.get(id=i.companyId)
        companies.append(company)
    
    posts = models.JobPosts.getAll(recruiterId=recruiter.id)
    
    print(companies)
    return render_template("/recruiter/index.html", recruiter=recruiter, companies=companies, posts=posts)


@recruiter.get("/login")
def login():
    return render_template("/recruiter/login.html")


@recruiter.get("/signup")
def signup():
    return render_template("/recruiter/signup.html")


@recruiter.get("/profile")
@jwt_required()
def profile():
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401
    
    recruiterModel = models.Recruiters.get(id=id)
    
    return render_template("/recruiter/profile.html", recruiter=recruiterModel)


@recruiter.get("/company/create")
@jwt_required()
def create_company():
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401
    
    
    return render_template("/recruiter/create_company.html")

@recruiter.get("/company/<id>")
@jwt_required()
def company(id):
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401 
    
    rc = models.RecruiterCompanies.get(recruiterId=id, companyId=id)
    
    if not rc:
        flash("Company not found", "error")
        return redirect(url_for("recruiter.index"))
    
    companyModel = models.Companies.get(id=id)
    
    if not companyModel:
        flash("Company not found", "error")
        return redirect(url_for("recruiter.index"))
    
    return render_template("/recruiter/company.html", recruiter=rc , company=companyModel)


@recruiter.get("/post/create")
@jwt_required()
def create_post():
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401
    
    
    recruiterCompanies = models.RecruiterCompanies.getAll(recruiterId=id)
    companies = []
    
    for i in recruiterCompanies:
        company = models.Companies.get(id=i.companyId)
        companies.append(company)
    
    print(companies)
    
    
    return render_template("/recruiter/create_post.html", companies=companies)


@recruiter.get("/post/<id>")
@jwt_required()
def post(id):
    cookie = get_jwt_identity()
    user_id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401
    
    recruiter = models.Recruiters.get(id=user_id)
    
    if not recruiter:
        return jsonify({"error": "Recruiter not found"}), 404
    
    post = models.JobPosts.get(id=id)
    
    if not post:
        return jsonify({"error": "Post not found"}), 404
    
    skills = []
    
    for post_skill in models.PostSkills.getAll(postId=id):
        skill = models.Skills.get(id=post_skill.skillId)
        if skill is None:
            continue
        skills.append(skill.model_dump())    
    
    return render_template("/recruiter/post.html",recruiter=recruiter , post=post, skills=skills)

