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


freelancer = Blueprint("freelancer", __name__)


@freelancer.get("/")
@jwt_required()
def index():
    # get current user
    cookie = get_jwt_identity()
    if not cookie:
        print("no cookie")
        return jsonify({"error": "Unauthorized"}), 401
    
    fid = int(cookie.split(',')[0])
    
    if cookie.split(',')[-1] != "freelancer":
        print("no freelancer")
        return jsonify({"error": "Unauthorized"}), 401
    
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
        "freelancer.html", freelancer=freelancer, 
        freelancerDetails=freelancerDetail, 
        educations=educations, experiences=experiences, 
        skills=skills
    )


@freelancer.get("/login")
def login():
    return render_template("login.html")


@freelancer.get("/signup")
def signup():
    return render_template("signup.html")