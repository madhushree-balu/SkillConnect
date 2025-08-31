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
    if not recruiter:
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
    if recruiter and recruiter.password == hashed_password:
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
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    
    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400
    
    if models.Recruiters.get(username=username):
        return jsonify({"error": "Username already exists"}), 400
    
    if models.Recruiters.get(email=email):
        return jsonify({"error": "Email already exists"}), 400
    
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    
    hashed_password = sha256(password.encode()).hexdigest()
    recruiter = models.Recruiters(username=username, email=email, password=hashed_password)
    rId = recruiter.insert()
    
    if not rId:
        return jsonify({"error": "Signup failed"}), 500
    
    recruiter = models.Recruiters.get(id=rId)
    
    if not recruiter:
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
    
    companies = models.RecruiterCompanies.getAll(recruiterId=id)
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
    
    if not data:
        return jsonify({"error": "Missing required fields"}), 400
    
    if not data.get("username") \
        or not data.get("companyName") \
            or not data.get("companyPhone") \
                or not data.get("companyAddress") \
                    or not data.get("companyDescription") \
                        or not data.get("employeeSize"):
        return jsonify({"error": "Missing required fields"}), 400
    
    company = models.Companies(
        username=data.get("username"),
        companyName=data.get("companyName"),
        companyPhone=data.get("companyPhone"),
        companyAddress=data.get("companyAddress"),
        companyDescription=data.get("companyDescription"),
        employeeSize=data.get("employeeSize")
    )
    
    # insert the company
    cId = company.insert()
    if not cId:
        return jsonify({"error": "Company creation failed"}), 500
    
    # try fetching the company details for further consistency
    company = models.Companies.get(id=cId)
    if not company:
        return jsonify({"error": "Company creation failed"}), 500
    
    # map the recruiter and company
    mapped = models.RecruiterCompanies(recruiterId=id, companyId=cId).insert()
    
    if mapped is None:
        # delete the company
        company.delete()
        return jsonify({"error": "Company created, but mapping failed. Please try again."}), 500
    
    return jsonify({"message": "Company created", "company": company}), 200
