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


recruiter_api = Blueprint("recruiter_api", __name__)


@recruiter_api.route("/", methods=["GET"])
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
    if recruiter is None:
        print("no get recruiter")
        return jsonify({"error": "Unauthorized"}), 401
    
    return jsonify({"message": "Recruiter API", "username": recruiter.username}), 200



@recruiter_api.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    hashed_password = sha256(password.encode()).hexdigest()
    
    recruiter = models.Recruiters.get(username=username)
    if recruiter is not None and recruiter.password == hashed_password:
        access_token = create_access_token(identity=f"{recruiter.id},recruiter")
        response = jsonify({
            "message": "Login successful",
        })
        set_access_cookies(response, access_token)   # store in cookie
        return response, 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401


@recruiter_api.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username").lower().strip()
    email = data.get("email").lower().strip()
    password = data.get("password")
    
    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400
    
    rec = models.Recruiters.get(username=username)
    if rec is not None:  # Changed: if user EXISTS, return error
        return jsonify({"error": "Username already exists"}), 400
    
    # Check if email already exists
    existing_email = models.Recruiters.get(email=email)
    if existing_email is not None:
        return jsonify({"error": "Email already exists"}), 400
    
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    
    hashed_password = sha256(password.encode()).hexdigest()
    recruiter = models.Recruiters(username=username, email=email, password=hashed_password)
    rId = recruiter.insert()
    
    if rId is None:
        return jsonify({"error": "Signup failed"}), 500
    
    recruiter = models.Recruiters.get(id=rId)
    
    if recruiter is None:
        return jsonify({"error": "Signup failed"}), 500
    
    access_token = create_access_token(identity=f"{recruiter.id},recruiter")

    response = jsonify({"message": "Signup successful", "access_token": access_token})
    set_access_cookies(response, access_token)   # store in cookie
    return response, 200


@recruiter_api.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200


@recruiter_api.get("/companies")
@jwt_required()
def companies():
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401
    
    companies = [i.model_dump() for i in models.RecruiterCompanies.getAll(recruiterId=id)]
    return jsonify({"companies": companies}), 200


@recruiter_api.post("/companies/<int:companyId>/join")
@jwt_required()
def add_company(companyId):
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401
    
    models.RecruiterCompanies(recruiterId=id, companyId=companyId).insert()
    return jsonify({"message": "Company added"}), 200

@recruiter_api.post("/companies/<int:companyId>/remove")
@jwt_required()
def remove_company(companyId):
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401
    
    models.RecruiterCompanies(recruiterId=id, companyId=companyId).delete()
    return jsonify({"message": "Company removed"}), 200


@recruiter_api.post("/companies/create")
@jwt_required()
def create_company():
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    
    if data is None:
        return jsonify({"error": "Missing required fields"}), 400
    
    if not data.get("username") \
        or not data.get("companyName") \
            or not data.get("companyPhone") \
                or not data.get("companyAddress") \
                    or not data.get("companyDescription") \
                        or not data.get("employeeSize"):
        return jsonify({"error": "Missing required fields"}), 400
    
    company = models.Companies(
        username=data.get("username").lower().strip(),
        companyName=data.get("companyName").strip(),
        companyPhone=data.get("companyPhone"),
        companyAddress=data.get("companyAddress"),
        companyDescription=data.get("companyDescription"),
        employeeSize=data.get("employeeSize")
    )
    
    # insert the company
    cId = company.insert()
    if cId is None:
        return jsonify({"error": "Company creation failed"}), 500
    
    # try fetching the company details for further consistency
    company = models.Companies.get(id=cId)
    if company is None:
        return jsonify({"error": "Company creation failed"}), 500
    
    # map the recruiter and company
    mapped = models.RecruiterCompanies(recruiterId=id, companyId=cId).insert()
    
    if mapped is None:
        # delete the company
        company.delete()
        return jsonify({"error": "Company created, but mapping failed. Please try again."}), 500
    
    return jsonify({"message": "Company created", "company": company.model_dump()}), 200


# Add these endpoints to your recruiter_api blueprint

@recruiter_api.route("/posts", methods=["GET"])
@jwt_required()
def get_all_posts():
    """Get all job posts for the authenticated recruiter"""
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401
    
    # Get all posts created by this recruiter
    posts = [post.model_dump() for post in models.JobPosts.getAll(recruiterId=id)]
    return jsonify({"posts": posts}), 200


@recruiter_api.route("/posts/<int:postId>", methods=["GET"])
@jwt_required()
def get_post(postId):
    """Get a specific job post by ID"""
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401
    
    post = models.JobPosts.get(id=postId)
    if post is None:
        return jsonify({"error": "Job post not found"}), 404
    
    # Verify the post belongs to this recruiter
    if post.recruiterId != int(id):
        return jsonify({"error": "Unauthorized"}), 401
    
    return jsonify({"post": post.model_dump()}), 200


@recruiter_api.route("/posts", methods=["POST"])
@jwt_required()
def create_post():
    """Create a new job post"""
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Missing required fields"}), 400
    
    # Validate required fields
    required_fields = ["companyId", "title", "description", "experience", "jobType", "location", "salary", "validTill", "skills"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Verify the recruiter has access to the specified company
    recruiter_company = models.RecruiterCompanies.get(recruiterId=id, companyId=data.get("companyId"))
    if recruiter_company is None:
        return jsonify({"error": "You don't have access to this company"}), 401
    
    # Create the job post
    job_post = models.JobPosts(
        recruiterId=int(id),
        companyId=data.get("companyId"),
        title=data.get("title").strip(),
        description=data.get("description").strip(),
        experience=data.get("experience"),
        jobType=data.get("jobType"),
        location=data.get("location").strip(),
        salary=data.get("salary"),
        validTill=data.get("validTill"),
        isActive=data.get("isActive", True)
    )
    
    post_id = job_post.insert()
    if post_id is None:
        return jsonify({"error": "Failed to create job post"}), 500
    
    # Fetch the created post
    created_post = models.JobPosts.get(id=post_id)
    if created_post is None:
        return jsonify({"error": "Job post created but failed to retrieve"}), 500
    
    splitSkills = data.get("skills").split(",")
    for s in splitSkills:
        skillModel = models.Skills.get_or_create(skill=s.strip())
        if not skillModel:
            continue
        
        skill = models.PostSkills(postId=post_id, skillId=skillModel.id).insert()
        if skill is None:
            return jsonify({"error": "Failed to create job post skill"}), 500
    
    return jsonify({"message": "Job post created successfully", "post": created_post.model_dump()}), 201


@recruiter_api.route("/posts/<int:postId>", methods=["PUT"])
@jwt_required()
def update_post(postId):
    """Update an existing job post"""
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401
    
    # Check if post exists and belongs to this recruiter
    post = models.JobPosts.get(id=postId)
    if post is None:
        return jsonify({"error": "Job post not found"}), 404
    
    if post.recruiterId != int(id):
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    if data is None:
        return jsonify({"error": "No data provided"}), 400
    
    # Filter out fields that shouldn't be updated
    allowed_fields = {"companyId", "title", "description", "experience", "jobType", "location", "salary", "validTill", "isActive"}
    update_data = {k: v for k, v in data.items() if k in allowed_fields and v is not None}
    
    if not update_data:
        return jsonify({"error": "No valid fields to update"}), 400
    
    # If companyId is being updated, verify access
    if "companyId" in update_data:
        recruiter_company = models.RecruiterCompanies.get(recruiterId=id, companyId=update_data["companyId"])
        if recruiter_company is None:
            return jsonify({"error": "You don't have access to this company"}), 401
    
    # Update the post
    result = post.update(**update_data)
    if result is None:
        return jsonify({"error": "Failed to update job post"}), 500
    
    # Fetch updated post
    updated_post = models.JobPosts.get(id=postId)
    if updated_post is None:
        return jsonify({"error": "Job post updated but failed to retrieve"}), 500
    
    return jsonify({"message": "Job post updated successfully", "post": updated_post.model_dump()}), 200


@recruiter_api.route("/posts/<int:postId>/skill/add", methods=["POST"])
@jwt_required()
def add_skill_to_post(postId):
    """Add a skill to a job post"""
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401
    
    # Check if post exists and belongs to this recruiter
    post = models.JobPosts.get(id=postId)
    if post is None:
        return jsonify({"error": "Job post not found"}), 404
    
    if post.recruiterId != int(id):
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    if data is None:
        return jsonify({"error": "No data provided"}), 400
    
    skillName = data.get("skillName")
    profeciencyLevel = data.get("proficiencyLevel")
    experience = data.get("experience")
    
    if not skillName or not profeciencyLevel or not experience:
        return jsonify({"error": "Missing required fields"}), 400
    
    skillModel = models.Skills.get_or_create(skill=skillName)
    
    skill = models.PostSkills(postId=postId, skillId=skillModel.id).insert()
    if skill is None:
        return jsonify({"error": "Failed to add skill to job post"}), 500
    
    return jsonify({"message": "Skill added to job post successfully"}), 200


@recruiter_api.route("/posts/<int:postId>/skill/remove", methods=["POST"])
@jwt_required()
def remove_skill_from_post(postId):
    """Remove a skill from a job post"""
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401
    
    # Check if post exists and belongs to this recruiter
    post = models.JobPosts.get(id=postId)
    if post is None:
        return jsonify({"error": "Job post not found"}), 404
    
    if post.recruiterId != int(id):
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    if data is None:
        return jsonify({"error": "No data provided"}), 400
    
    skill = models.PostSkills(postId=postId, skillId=data.get("skillId")).delete()
    if skill is None:
        return jsonify({"error": "Failed to remove skill from job post"}), 500
    
    return jsonify({"message": "Skill removed from job post successfully"}), 200


@recruiter_api.route("/posts/<int:postId>", methods=["DELETE"])
@jwt_required()
def delete_post(postId):
    """Delete a job post"""
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401
    
    # Check if post exists and belongs to this recruiter
    post = models.JobPosts.get(id=postId)
    if post is None:
        return jsonify({"error": "Job post not found"}), 404
    
    if post.recruiterId != int(id):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Delete the post
    result = post.delete()
    if result is None:
        return jsonify({"error": "Failed to delete job post"}), 500
    
    return jsonify({"message": "Job post deleted successfully"}), 200


@recruiter_api.route("/posts/company/<int:companyId>", methods=["GET"])
@jwt_required()
def get_posts_by_company(companyId):
    """Get all job posts for a specific company"""
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401
    
    # Verify the recruiter has access to this company
    recruiter_company = models.RecruiterCompanies.get(recruiterId=id, companyId=companyId)
    if recruiter_company is None:
        return jsonify({"error": "You don't have access to this company"}), 401
    
    # Get all posts for this company created by this recruiter
    posts = [post.model_dump() for post in models.JobPosts.getAll(recruiterId=id, companyId=companyId)]
    return jsonify({"posts": posts}), 200


@recruiter_api.route("/posts/<int:postId>/toggle-status", methods=["POST"])
@jwt_required()
def toggle_post_status(postId):
    """Toggle the active status of a job post"""
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401
    
    # Check if post exists and belongs to this recruiter
    post = models.JobPosts.get(id=postId)
    if post is None:
        return jsonify({"error": "Job post not found"}), 404
    
    if post.recruiterId != int(id):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Toggle the status
    new_status = not post.isActive
    result = post.update(isActive=new_status)
    
    if result is None:
        return jsonify({"error": "Failed to update job post status"}), 500
    
    status_text = "activated" if new_status else "deactivated"
    return jsonify({"message": f"Job post {status_text} successfully", "isActive": new_status}), 200