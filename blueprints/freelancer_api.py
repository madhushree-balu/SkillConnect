from flask import (
    Blueprint, request, jsonify, abort, send_file,
    current_app as app, redirect, flash, get_flashed_messages,
    url_for, session
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


freelancer_api = Blueprint("freelancer_api", __name__)


@freelancer_api.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    hashed_password = sha256(password.encode()).hexdigest()
    
    freelancer = models.Freelancers.get(username=username)
    if freelancer and freelancer.password == hashed_password:
        access_token = create_access_token(identity=f"{freelancer.id},freelancer")
        response = jsonify({
            "message": "Login successful",
        })
        set_access_cookies(response, access_token)   # store in cookie
        return response, 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401


@freelancer_api.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    
    if username is None or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400
    
    if models.Freelancers.get(username=username):
        return jsonify({"error": "Username already exists"}), 400
    
    if models.Freelancers.get(email=email):
        return jsonify({"error": "Email already exists"}), 400
    
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    
    hashed_password = sha256(password.encode()).hexdigest()
    freelancer = models.Freelancers(username=username, email=email, password=hashed_password)
    fId = freelancer.insert()
    
    if fId is None:
        return jsonify({"error": "Signup failed"}), 500
    
    freelancer = models.Freelancers.get(id=fId)
    freelancerDetail = models.FreelancerDetails(
        freelancerId=fId,
        firstName=data.get("firstName", ""),
        middleName=data.get("middleName", ""),
        lastName=data.get("lastName", ""),
        phoneNumber=data.get("phoneNumber", ""),
        contactEmail=data.get("contactEmail", ""),
        about=data.get("about", ""),
        dateOfBirth=data.get("dateOfBirth", ""),
        address=data.get("address", "")
    )
    fdId = freelancerDetail.insert()
    
    if freelancer is None:
        return jsonify({"error": "Signup failed"}), 500
    
    if fdId is None:
        freelancer.delete()
        return jsonify({"error": "Signup failed"}), 500
    
    access_token = create_access_token(identity=f"{freelancer.id},freelancer")
    response = jsonify({
        "message": "Signup successful",
    })
    set_access_cookies(response, access_token)
    
    return response, 200


@freelancer_api.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200


@freelancer_api.route("/", methods=["GET"])
@jwt_required()
def index():
    # get current user
    cookie = get_jwt_identity()
    if cookie is None:
        print("no cookie")
        return jsonify({"error": "Unauthorized"}), 401
    
    if cookie.split(',')[-1] != "freelancer":
        print("no freelancer")
        return jsonify({"error": "Unauthorized"}), 401
    
    freelancer = models.Freelancers.get(id=int(cookie.split(',')[0]))
    print(cookie)
    if freelancer is None:
        print("no get freelancer")
        return jsonify({"error": "Unauthorized"}), 401
    
    return jsonify({"message": "Freelancer API", "username": freelancer.username}), 200


@freelancer_api.get("/profile")
@jwt_required()
def profile():
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    id = int(id)
    print(cookie)
    
    if role != "freelancer":
        return jsonify({"error": "Unauthorized"}), 401
    
    freelancer = models.Freelancers.get(id=id)
    freelancerDetails = models.FreelancerDetails.get(freelancerId=id)
    educations = models.Educations.getAll(freelancerId=id)
    experiences = models.Experiences.getAll(freelancerId=id)
    rawSkills = models.FreelancerSkills.getAll(freelancerId=id)
    skills = []
    
    if freelancer is None:
        print("no freelancer")
        return jsonify({"error": "Unauthorized"}), 401
    else:
        freelancer = freelancer.model_dump()
    
    if freelancerDetails is None:
        print("no freelancer details")
        return jsonify({"error": "Unauthorized"}), 401
    else:
        freelancerDetails = freelancerDetails.model_dump()
    
    if educations:
        educations = [edu.model_dump() for edu in educations]
    else:
        educations = []
        
    if experiences:
        experiences = [exp.model_dump() for exp in experiences]
    else:
        experiences = []
        
    if rawSkills:
        rawSkills = [skill.model_dump() for skill in rawSkills]
    else:
        rawSkills = []
    
    for skill in rawSkills:
        skillClass = models.Skills.get(id=skill["skillId"])
        if skillClass is not None:
            skills.append({"skill": skillClass.model_dump(), "proficiencyLevel": skill["proficiencyLevel"], "yearsOfExperience": skill["yearsOfExperience"]})
    
    return jsonify({"freelancer": freelancer, "freelancerDetails": freelancerDetails, "educations": educations, "experiences": experiences, "skills": skills}), 200


@freelancer_api.post("/profile/details/update")
@jwt_required()
def update_freelancer_details():
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    id = int(id)
    print(cookie)
    if role != "freelancer":
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    oldDetails = models.FreelancerDetails.get(freelancerId=id)
    print(oldDetails)
    if oldDetails is None:
        print("no old details")
        return jsonify({"error": "Profile update failed"}), 500
    freelancerDetails = models.FreelancerDetails(
        id=oldDetails.id,
        freelancerId=id,
        firstName = data.get("firstName"),
        middleName = data.get("middleName"),
        lastName = data.get("lastName"),
        phoneNumber = data.get("phoneNumber"),
        contactEmail = data.get("contactEmail"),
        about = data.get("about"),
        dateOfBirth = data.get("dateOfBirth"),
        address = data.get("address"),
    )
    updated = freelancerDetails.update()
    if updated is None:
        return jsonify({"error": "Profile update failed"}), 500
    
    return jsonify({"message": "Profile updated"}), 200


@freelancer_api.post("/profile/skills/add")
@jwt_required()
def add_freelancer_skill():
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "freelancer":
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    print(data)
    skill = data.get("skillName")
    print(skill)
    skillClass = models.Skills.get_or_create(skill)
    if skillClass is None:
        return jsonify({"error": "Skill add failed"}), 500
    
    skillId = skillClass.id
    
    freelancerSkill = models.FreelancerSkills(
        freelancerId=id,
        skillId = skillId,
        proficiencyLevel = data.get("proficiencyLevel"),
        yearsOfExperience = data.get("yearsOfExperience")
    )
    added = freelancerSkill.insert()
    
    if added is None:
        return jsonify({"error": "Skill add failed"}), 500
    
    return jsonify({"message": "Skill added"}), 200


@freelancer_api.post("/profile/skills/delete")
@jwt_required()
def delete_freelancer_skill():
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "freelancer":
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    freelancerSkill = models.FreelancerSkills(
        freelancerId=int(id),
        skillId = int(data.get("skillId"))
    )
    deleted = freelancerSkill.delete(freelancerId=int(id), skillId=int(data.get("skillId")))
    
    if deleted is None:
        return jsonify({"error": "Skill delete failed"}), 500
    
    return jsonify({"message": "Skill deleted"}), 200


@freelancer_api.post("/profile/educations/add")
@jwt_required()
def add_freelancer_education():
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "freelancer":
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    education = models.Educations(
        freelancerId=id,
        school = "",
        degree = "",
        startDate = "",
        endDate = "",
        cgpa = 0.0,
        course = ""
    )
    added = education.insert()
    
    if added is None:
        return jsonify({"error": "Education add failed"}), 500
    
    return jsonify({"message": "Education added"}), 200


@freelancer_api.post("/profile/educations/delete")
@jwt_required()
def delete_freelancer_education():
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "freelancer":
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    education = models.Educations.get(id=data.get("id"))
    
    if education is None:
        return jsonify({"error": "Education not found"}), 404
    
    deleted = education.delete()
    
    if deleted is None:
        return jsonify({"error": "Education delete failed"}), 500
    
    return jsonify({"message": "Education deleted"}), 200


@freelancer_api.post("/profile/educations/update")
@jwt_required()
def update_freelancer_education():
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "freelancer":
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    education = models.Educations.get(id=data.get("id"))
    
    if education is None:
        return jsonify({"error": "Education not found"}), 404
    
    education.school = data.get("school")
    education.degree = data.get("degree")
    education.startDate = data.get("startDate")
    education.endDate = data.get("endDate")
    education.cgpa = float(data.get("cgpa", 0.0))
    education.course = data.get("course")
    updated = education.update()
    
    if updated is None:
        return jsonify({"error": "Education update failed"}), 500
    
    return jsonify({"message": "Education updated"}), 200


@freelancer_api.post("/profile/experiences/add")
@jwt_required()
def add_freelancer_experience():
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "freelancer":
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    experience = models.Experiences(
        freelancerId=id,
        companyName = data.get("company"),
        role = data.get("role"),
        startDate = data.get("startDate"),
        endDate = data.get("endDate"),
        description = data.get("description")
    )
    added = experience.insert()
    
    if added is None:
        return jsonify({"error": "Experience add failed"}), 500
    
    return jsonify({"message": "Experience added"}), 200


@freelancer_api.post("/profile/experiences/delete")
@jwt_required()
def delete_freelancer_experience():
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "freelancer":
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    experience = models.Experiences.get(id=data.get("id"))
    
    if experience is None:
        return jsonify({"error": "Experience not found"}), 404
    
    deleted = experience.delete()
    
    if deleted is None:
        return jsonify({"error": "Experience delete failed"}), 500
    
    return jsonify({"message": "Experience deleted"}), 200


@freelancer_api.post("/profile/experiences/update")
@jwt_required()
def update_freelancer_experience():
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "freelancer":
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    experience = models.Experiences.get(id=data.get("id"))
    
    if experience is None:
        return jsonify({"error": "Experience not found"}), 404
    
    experience.companyName = data.get("company")
    experience.role = data.get("role")
    experience.startDate = data.get("startDate")
    experience.endDate = data.get("endDate")
    experience.description = data.get("description")
    updated = experience.update()
    
    if updated is None:
        return jsonify({"error": "Experience update failed"}), 500
    
    return jsonify({"message": "Experience updated"}), 200