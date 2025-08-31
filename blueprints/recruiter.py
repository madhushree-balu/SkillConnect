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
    
    companies = models.RecruiterCompanies.getAll(recruiterId=recruiter.id)
    posts = models.JobPosts.getAll(recruiterId=recruiter.id)
    
    return render_template("recruiter.html", recruiter=recruiter, companies=companies, posts=posts)


@recruiter.get("/login")
def login():
    return render_template("login.html")


@recruiter.get("/signup")
def signup():
    return render_template("signup.html")

@recruiter.get("/company/create")
@jwt_required()
def create_company():
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401
    
    return render_template("create_company.html")

@recruiter.get("/company/<id>")
@jwt_required()
def company(id):
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401 
    
    return render_template("company.html")


@recruiter.get("/post/create")
@jwt_required()
def create_post():
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401
    
    return render_template("create_post.html")


@recruiter.get("/post/<id>")
@jwt_required()
def post(id):
    cookie = get_jwt_identity()
    id, role = cookie.split(',')
    
    if role != "recruiter":
        return jsonify({"error": "Unauthorized"}), 401
    
    post = models.JobPosts.get(id=id)
    
    if not post:
        return jsonify({"error": "Post not found"}), 404
    
    return render_template("post.html", post=post)
