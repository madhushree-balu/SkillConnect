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
            <span>${skill}</span>
            <div class="skillRemove">
                <button class="removeSkill" skillId="${newSkillId}">✕</button>
            </div>
        `;
        skillContainer.appendChild(newSkillElement);
        newSkill.value = "";
    })
}

document.getElementById("newSkill").addEventListener("keyup", function(event) {
    if (event.key === "Enter") {
        addSkill();
    }
});


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
                            <div class="inputField">
                                <label for="exp-company-${experienceId}">Company</label>
                                <input type="text" id="exp-company-${experienceId}" class="company" placeholder="Company" />
                            </div>
                            <div class="inputField">
                                <label for="exp-position-${experienceId}">Position</label>
                                <input type="text" id="exp-position-${experienceId}" class="position" placeholder="Position" />
                            </div>
                        </div>
                        <div class="dates">
                            <div class="inputField">
                                <label for="exp-start-${experienceId}">Start Date</label>
                                <input type="date" id="exp-start-${experienceId}" name="startDate" class="startDate"  />
                            </div>
                            <div class="inputField">
                                <label for="exp-end-${experienceId}">End Date</label>
                                <input type="date" id="exp-end-${experienceId}" name="endDate" class="endDate"  />
                            </div>
                        </div>
                        <div class="inputField">
                            <label for="exp-desc-${experienceId}">Description</label>
                            <textarea id="exp-desc-${experienceId}" name="description" class="description"></textarea>
                        </div>
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

                newEducationElement.innerHTML = `
                    <div class="educationContainer">
                        <div class="degreeMark">

                        <div class="inputField">
                            <label for="edu-school-${json["educationId"]}">School</label>    
                        <input type="text" id="edu-school-${json["educationId"]}" class="school" placeholder="School" />
                        </div>
                            <div class="inputField">
                            <label for="edu-degree-${json["educationId"]}">School</label>
                            <input type="text" id="edu-degree-${json["educationId"]}" class="degree" placeholder="Degree" />
                            </div>
                            <div class="inputField">
                            <label for="edu-fos-${json["educationId"]}">School</label>
                            <input type="text" id="edu-fos-${json["educationId"]}" class="fieldOfStudy" placeholder="Field Of Study" />
                            </div>
                        </div>
                        <div class="dates">
                        <div class="inputField">
                            <label for="edu-start-${json["educationId"]}">School</label>    
                        <input type="date" id="edu-start-${json["educationId"]}" name="startDate" class="startDate"  />
                        </div>
                            <div class="inputField">
                            <label for="edu-end-${json["educationId"]}">School</label>
                            <input type="date" id="edu-end-${json["educationId"]}" name="endDate" class="endDate"  />
                            </div>
                        </div>
                        <div class="inputField">
                            <label for="edu-cgpa-${json["educationId"]}">School</label>
                        <input type="number" id="edu-cgpa-${json["educationId"]}" name="cgpa" class="cgpa"  />
                        </div>
                    </div>
                    <div class="buttons">
                        <div class="removeBtn">
                            <button class="removeEducation" educationId="${json["educationId"]}" onclick="removeEducation(this)">Remove</button>
                        </div>
                        <div class="saveButton">
                            <button class="saveEducation" educationId="${json["educationId"]}" onclick="saveEducation(this)">Save</button>
                        </div>
                    </div>
                `;
                educationContainer.appendChild(newEducationElement);

            })
    })
}

function removeEducation(e) {
    var educationId = e.getAttribute("educationId");
    fetch("/api/education/remove", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            educationId: educationId
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

function saveEducation(e) {
    var educationId = e.getAttribute("educationId");
    var school = document.getElementById(`edu-school-${educationId}`).value;
    var degree = document.getElementById(`edu-degree-${educationId}`).value;
    var fieldOfStudy = document.getElementById(`edu-fos-${educationId}`).value;
    var start = document.getElementById(`edu-start-${educationId}`).value;
    var end = document.getElementById(`edu-end-${educationId}`).value;
    var cgpa = document.getElementById(`edu-cgpa-${educationId}`).value;

    fetch("/api/education/modify", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            educationId: educationId,
            school: school,
            degree: degree,
            startDate: start,
            endDate: end,
            cgpa: cgpa,
            fieldOfStudy: fieldOfStudy
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

function saveProfile() {
    var firstName = document.getElementById("firstName").value;
    var middleName = document.getElementById("middleName").value;
    var lastName = document.getElementById("lastName").value;
    var summary = document.getElementById("summary").value;
    var phoneNumber = document.getElementById("phoneNumber").value;
    var address = document.getElementById("address").value;
    var personalWebsite = document.getElementById("personalWebsite").value;
    var contactEmail = document.getElementById("contactEmail").value;

    fetch("/api/profile/modify", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            firstName: firstName,
            middleName: middleName,
            lastName: lastName,
            summary: summary,
            phoneNumber: phoneNumber,
            address: address,
            personalWebsite: personalWebsite,
            contactEmail: contactEmail
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