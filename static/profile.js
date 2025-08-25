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
            <span>${ skill }<span/>
            <div class="skillRemove">
                <button class="removeSkill" skillId="${ newSkillId }">X</button>
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
            newExperienceElement.setAttribute("experienceId", json["experienceId"]);
            newExperienceElement.innerHTML = `
                <div class="experienceRemove">
                    <button class="removeExp-erience" experienceId="${ json["experienceId"] }">X</button>
                </div>
            `;
            experienceContainer.appendChild(newExperienceElement);
        })
    })

}