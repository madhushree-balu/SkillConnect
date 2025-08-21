from flask import (
    Blueprint, flash, redirect, render_template, 
    request, session, url_for
)
from handler import models, db


api = Blueprint('api', __name__, url_prefix='/api')


@api.get("/")
def index():
    return {
        "success": True
    }