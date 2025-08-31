from flask import Flask
from db import models, database_setup

from flask import Flask
from flask_jwt_extended import JWTManager

from blueprints.recruiter_api import recruiter_api
from blueprints.freelancer_api import freelancer_api

def create_app():
    app = Flask(__name__)
    
    if not database_setup.check_database_status():
        database_setup.create_database()
    
    # Secret key for JWT
    app.config["JWT_SECRET_KEY"] = "DO YOU KNOW FLASK??"
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_SECURE"] = False          # Set True in production (HTTPS only)
    app.config["JWT_COOKIE_CSRF_PROTECT"] = True     # Extra CSRF protection
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Register blueprint
    app.register_blueprint(recruiter_api, url_prefix="/api/recruiter")
    app.register_blueprint(freelancer_api, url_prefix="/api/freelancer")
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

