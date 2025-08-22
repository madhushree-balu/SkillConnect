from flask import (
    Flask, request, session, url_for,
    render_template, redirect
)
import re
from handler import db, models, utils

app = Flask(__name__)
app.secret_key = "My Secret Key"


sessionHandler = db.SessionHandler()

@app.before_request
def before_request():
    userId = session.get("userId")
    ip = request.remote_addr
    if userId is None:
        sessionId = utils.hash_password(str(userId) + str(request.remote_addr))
        sessionUserId = sessionHandler.get_session(sessionId)
        if re.fullmatch('^(auth|api|index|static)', request.endpoint) or sessionUserId == userId:
            return redirect(url_for("auth.login"))


@app.get("/")
def index():
    userId = session.get("userId", None)
    return render_template("index.html")


@app.get("/profile")
def profile():
    return render_template("profile.html")


if __name__ == "__main__":
    app.run(debug=True)