from flask import (
    Flask, request, session, url_for,
    render_template, redirect
)
import re
from handler import db, models, utils

app = Flask(__name__)
app.secret_key = "My Secret Key"


@app.before_request
def before_request():
    if session.get("sessionId") is None:
        if re.fullmatch('^(auth|api|index|static)', request.endpoint):
            return redirect(url_for("auth.login"))



@app.get("/")
def index():
    return {
        "success": True,
        
    }


@app.get("/profile")
def profile():
    return {
        "success": True,
        
    }


if __name__ == "__main__":
    app.run(debug=True)