from flask import (
    Flask, request, session, url_for,
    render_template, redirect
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
    if request.endpoint == 'index':
        return
    
    # If user is not logged in, redirect to login
    if userId is None:
        return redirect(url_for("auth.login"))
    
    # Optional: Session validation using IP (uncomment if needed)
    sessionId = utils.hash_password(str(userId) + str(ip))
    sessionUserId = sessionHandler.get_session(sessionId)
    if sessionUserId != userId:
        session.clear()
        return redirect(url_for("auth.login"))


@app.get("/")
def index():
    userId = session.get("userId", None)
    return render_template("index.html")


@app.get("/profile")
def profile():
    return render_template("profile.html")


app.register_blueprint(api.api)
app.register_blueprint(auth.auth)


if __name__ == "__main__":
    app.run(debug=True)