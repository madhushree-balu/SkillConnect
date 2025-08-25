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



@api.post("/education/create")
def create_education():

    userId=session.get("userId")
    emptyEducation = models.Education(
        userId = userId,
    )

    education = db.UserHandler().add_education(userId, emptyEducation)

    if education:
        return {
            "success": True,
            "educationId": education.educationId
        }

    return {
        "success": False,
        "error": "Could not create new education!"
    }

@api.post("/education/modify")
def modify_education():
    userId = session.get("userId")
    data = request.get_json()

    updatedEducation = models.Education(
        educationId = data["educationId"],
        userId = userId,
        school = data["school"],
        degree = data["degree"],
        fieldOfStudy = data["fieldOfStudy"],
        startDate = data["startDate"],
        endDate = data["endDate"],
        cgpa = data["cgpa"]
    )

    education = db

    
@api.post("/experience/create")
def create_experience():

    userId = session.get("userId")
    emptyExperience = models.Experience(
        userId = userId
    )

    experience = db.UserHandler().add_experience(userId, emptyExperience)

    if experience:
        return {
            "success": True,
            "experienceId": experience.experienceId
        }

    return {
        "success": False,
        "error": "Could not create new experience!"
    }
