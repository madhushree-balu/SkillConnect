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


@api.post("/profile/modify")
def modify_user_profile():
    userId = session.get("userId")
    
    if userId is None:
        return {
            "success": False,
            "error": "User is not logged in!"
        }
    
    data = request.get_json()
    
    userProfile = models.UserProfile(
        userId=userId,
        firstName=data.get("firstName"),
        middleName=data.get("middleName"),
        lastName=data.get("lastName"),
        summary=data.get("summary"),
        phoneNumber=data.get("phoneNumber"),
        address=data.get("address"),
        personalWebsite=data.get("personalWebsite"),
        contactEmail=data.get("contactEmail")
    )
    
    updatedUserProfile = db.UserHandler().update_user_profile(userProfile)
    
    if updatedUserProfile:
        return {
            "success": True
        }
    
    return {
        "success": False,
        "error": "Could not update profile!"
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
    
    if not userId:
        return {
            "success": False,
            "error": "User is not logged in!"
        }
    
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

    if userId is None:
        return {
            "success": False,
            "error": "User is not logged in!"
        }

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

    education = db.UserHandler().update_education(updatedEducation)
    
    if education:
        return {
            "success": True
        }

    return {
        "success": False,
        "error": "Could not update education!"
    }


@api.post("/education/remove")
def remove_education():
    form = request.get_json(force=True)
    educationId = form.get("educationId")
    
    if educationId is None:
        return {
            "success": False,
            "error": "Education ID is required"
        }
    
    return {
        "success": db.UserHandler().remove_education(session["userId"], educationId)
    }

    
@api.post("/experience/create")
def create_experience():

    userId = session.get("userId")
    
    if userId is None:
        return {
            "success": False,
            "error": "User is not logged in!"
        }
    
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


@api.post("/experience/modify")
def modify_experience():
    userId = session.get("userId")
    data = request.get_json()

    if userId is None:
        return {
            "success": False,
            "error": "User is not logged in!"
        }

    updatedExperience = models.Experience(
        experienceId = data["experienceId"],
        userId = userId,
        company = data["company"],
        position = data["position"],
        startDate = data["startDate"],
        endDate = data["endDate"],
        description = data["description"]
    )

    experience = db.UserHandler().update_experience(updatedExperience)
    
    if experience:
        return {
            "success": True
        }

    return {
        "success": False,
        "error": "Could not update experience!"
    }


@api.post("/experience/remove")
def remove_experience():
    form = request.get_json(force=True)
    experienceId = form.get("experienceId")
    
    if experienceId is None:
        return {
            "success": False,
            "error": "Experience ID is required"
        }
    
    return {
        "success": db.UserHandler().remove_experience(session["userId"], experienceId)
    }