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
    
    
@api.post("/skills/add")
def add_skill():
    form = request.get_json(force=True)
    skill = form.get("skill")
    
    if skill is None or skill == "":
        return {
            "success": False,
            "error": "Skill is required"
        }

    userSkill = db.UserSkillHandler().add_user_skill(session["userId"], skill)
    
    if userSkill is None:
        return {
            "success": False,
            "error": "Skill already exists"
        }
    
    return {
        "success": True,
        "skillId": userSkill.skillId,
        "skill": skill
    }
    
@api.post("/skills/remove")
def remove_skill():
    
    form = request.get_json(force=True)
    skillId = form.get("skillId")
    
    if skillId is None:
        return {
            "success": False,
            "error": "Skill ID is required"
        }
    
    return {
        "success": db.UserSkillHandler().remove_user_skill(session["userId"], skillId)
    }