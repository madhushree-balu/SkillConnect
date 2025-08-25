function addSkill() {
    var newSkill = document.getElementById("newSkill");
    var skill = newSkill.value.trim();

    if (skill === "") {
        return;
    }

    var skillContainer = document.querySelector("#skills .container");
    var newSkillElement = document.createElement("div");
    newSkillElement.className = "skillField";

    fetch("/api/skills/add", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            skill: skill
        })

    }).then(function (response) {
        data = response.json();
        return data;
    }).then(function (data) {
        if (data["success"] == false) {
            alert(data["error"]);
            return;
        }
        var newSkillId = data["skillId"];
        newSkillElement.setAttribute("skillId", newSkillId);
        newSkillElement.innerHTML = `
            <span>${skill}<span/>
            <div class="skillRemove">
                <button class="removeSkill" skillId="${newSkillId}">X</button>
            </div>
        `;
        skillContainer.appendChild(newSkillElement);
    })
}


function removeSkill(e) {
    var skillId = e.getAttribute("skillId");
    fetch("/api/skills/remove", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            skillId: skillId
        })
    }).then(response => {
        response.json().then(json => {
            if (json["success"] == false) {
                alert(json["error"]);
                return;
            }
            e.parentNode.parentNode.remove();
        })
    })
}


function addExperience() {
    var experienceContainer = document.querySelector("#experiences .container");
    var newExperienceElement = document.createElement("div");
    newExperienceElement.className = "experienceField";

    fetch("/api/experience/create", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        }
    }).then(response => {
        response.json().then(json => {
            if (json["success"] == false) {
                alert(json["error"]);
                return;
            }
            var experienceId = json["experienceId"];
            newExperienceElement.setAttribute("experienceId", experienceId);
            newExperienceElement.innerHTML = `
                <div class="experienceContainer">
                        <div class="companyRole">
                            <input type="text" id="exp-company-${experienceId}" class="company" placeholder="Company" />
                            <input type="text" id="exp-position-${experienceId}" class="position" placeholder="Position" />
                        </div>
                        <div class="dates">
                            <input type="date" id="exp-start-${experienceId}" name="startDate" class="startDate"  />
                            <input type="date" id="exp-end-${experienceId}" name="endDate" class="endDate"  />
                        </div>
                        <textarea id="exp-desc-${experienceId}" name="description" class="description">
                        </textarea>
                    </div>
                    <div class="buttons">
                        <div class="removeBtn">
                            <button class="removeExperience" experienceId="${experienceId}" onclick="removeExperience(this)">Remove</button>
                        </div>
                        <div class="saveButton">
                            <button class="saveExperience" experienceId="${experienceId}" onclick="saveExperience(this)">Save</button>
                        </div>
                    </div>

            `;
            experienceContainer.appendChild(newExperienceElement);
        })
    })

}

function saveExperience(e) {
    var experienceId = e.getAttribute("experienceId");
    var company = document.getElementById(`exp-company-${experienceId}`).value;
    var position = document.getElementById(`exp-position-${experienceId}`).value;
    var description = document.getElementById(`exp-desc-${experienceId}`).value;
    var start = document.getElementById(`exp-start-${experienceId}`).value;
    var end = document.getElementById(`exp-end-${experienceId}`).value;

    fetch("/api/experience/modify", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            experienceId: experienceId,
            company: company,
            position: position,
            description: description,
            startDate: start,
            endDate: end
        })
    }).then(response => {
        return response.json()
    }).then(json => {

        if (json["success"] == false) {
            alert(json["error"]);
            return;
        }
        alert("Saved!");
        return;
    })

}


function removeExperience(e) {
    var experienceId = e.getAttribute("experienceId");
    fetch("/api/experience/remove", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            experienceId: experienceId
        })
    }).then(response => {
        return response.json()
    }).then(json => {
        if (json["success"] == false) {
            alert(json["error"]);
            return;
        }
        e.parentNode.parentNode.parentNode.remove();
        return;
    })
}

function addEducation() {
    var educationContainer = document.querySelector("#educations .container");
    var newEducationElement = document.createElement("div");
    newEducationElement.className = "educationField";

    fetch("/api/education/create", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        }
    }).then(response => {
        response.json()
            .then(json => {
                if (json["success"] == false) {
                    alert(json["error"]);
                    return;
                }
            })
    })
}