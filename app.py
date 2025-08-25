from flask import (
    Flask, request, session, url_for,
    render_template, redirect, flash, get_flashed_messages
)
import re
from handler import db, models, utils

from blueprints import api, auth

app = Flask(__name__)
app.secret_key = "My Secret Key"

db.DB().create_tables()
sessionHandler = db.SessionHandler()

@app.before_request
def before_request():
    userId = session.get("userId")
    ip = request.remote_addr
    
    print(f"userId: {userId}, ip: {ip}")
    print(request.endpoint)
    
    # Skip authentication for static files and auth endpoints
    if request.endpoint and re.match(r'^(auth\.|api\.|static).*', request.endpoint):
        return
    
    # Allow access to index page
    if request.endpoint == 'index' or request.endpoint is None:
        return
    
    # If user is not logged in, redirect to login
    if userId is None:
        return redirect(url_for("auth.login"))
    
    # Optional: Session validation using IP (uncomment if needed)
    sessionId = utils.hash_password(str(userId) + str(ip))
    dbSession = sessionHandler.get_session(sessionId)
    
    if not dbSession:
        session.clear()
        flash("Invalid Session!", "error")
        return redirect(url_for("auth.login"))
    
    if dbSession.userId != userId:
        session.clear()
        flash("Invalid Session!", "error")
        
        return redirect(url_for("auth.login"))


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/profile")
def profile():
    userId = session.get("userId", None)
    
    
    if userId is None:
        session.clear()
        flash("Please log in first", "error")
        return redirect(url_for("auth.login"))
    
    userHandler = db.UserHandler()
    user = userHandler.get_user(userId)

    if user is None:
        session.clear()
        flash("User not found", "error")
        return redirect(url_for("auth.login"))

    profile = userHandler.get_user_profile(userId)
    
    if profile is None:
        profile = userHandler.create_user_profile(models.UserProfile(userId=userId))
    
    if not profile:
        session.clear()
        flash("Could not create profile!", "error")
        return redirect(url_for("auth.login"))
    
    
    education = userHandler.get_educations(userId) or []
    experience = userHandler.get_experiences(userId) or []
    skills = userHandler.get_user_skills_with_names(userId) or []

    return render_template("profile.html", user=user, profile=profile, education=education, experience=experience, skills=skills)


app.register_blueprint(api.api)
app.register_blueprint(auth.auth)


if __name__ == "__main__":
    app.run(debug=True)