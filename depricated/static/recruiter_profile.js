function saveProfile() {
    var name = document.getElementById("name").value;
    var email = document.getElementById("email").value;
    var company = document.getElementById("company").value;
    var location = document.getElementById("location").value;
    var website = document.getElementById("website").value;
    var contactEmail = document.getElementById("contactEmail").value;
    var contactNumber = document.getElementById("contactNumber").value;

    fetch("/recruiter/api/profile/modify", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name: name,
            email: email,
            company: company,
            location: location,
            website: website,
            contact_email: contactEmail,
            contact_number: contactNumber
        })
    }).then(response => {
        return response.json()
    }).then(json => {
        if (json["success"] == false) {
            alert(json["error"]);
            return;
        }
        alert("Profile saved!");
        return;
    })
}

function addJob() {
    fetch("/recruiter/api/jobs/create", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        }
    }).then(response => {
        return response.json()
    }).then(json => {
        if (json["success"] == false) {
            alert(json["error"]);
            return;
        }
        
        // Redirect to job creation form or refresh page
        window.location.href = `/recruiter/jobs/${json.jobId}/edit`;
    })
}

function saveJob(e) {
    var jobId = e.getAttribute("jobId");
    var title = document.getElementById(`job-title-${jobId}`).value;
    var location = document.getElementById(`job-location-${jobId}`).value;
    var salary = document.getElementById(`job-salary-${jobId}`).value;
    var experience = document.getElementById(`job-experience-${jobId}`).value;
    var description = document.getElementById(`job-description-${jobId}`).value;

    fetch("/recruiter/api/jobs/modify", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            jobId: jobId,
            title: title,
            location: location,
            salary: parseFloat(salary) || 0.0,
            experience: parseInt(experience) || 0,
            description: description
        })
    }).then(response => {
        return response.json()
    }).then(json => {
        if (json["success"] == false) {
            alert(json["error"]);
            return;
        }
        alert("Job saved!");
        return;
    })
}

function removeJob(e) {
    var jobId = e.getAttribute("jobId");
    
    if (!confirm("Are you sure you want to delete this job? This will also remove all applications for this job.")) {
        return;
    }

    fetch("/recruiter/api/jobs/remove", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            jobId: jobId
        })
    }).then(response => {
        return response.json()
    }).then(json => {
        if (json["success"] == false) {
            alert(json["error"]);
            return;
        }
        e.closest('.jobField').remove();
        alert("Job deleted successfully!");
    })
}

function addJobSkill(e) {
    var jobId = e.getAttribute("jobId");
    var skillInput = e.parentNode.querySelector('.newJobSkill');
    var skill = skillInput.value.trim();

    if (skill === "") {
        return;
    }

    fetch("/recruiter/api/jobs/skills/add", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            jobId: jobId,
            skill: skill
        })
    }).then(response => {
        return response.json()
    }).then(json => {
        if (json["success"] == false) {
            alert(json["error"]);
            return;
        }

        var skillsContainer = e.parentNode.parentNode.querySelector('.skillsContainer');
        var newSkillElement = document.createElement("div");
        newSkillElement.className = "skillTag";
        newSkillElement.setAttribute("skillId", json.skillId);
        newSkillElement.innerHTML = `
            <span>${skill}</span>
            <button class="removeJobSkill" jobId="${jobId}" skillId="${json.skillId}" onclick="removeJobSkill(this)">✕</button>
        `;
        skillsContainer.appendChild(newSkillElement);
        skillInput.value = "";
    })
}

function removeJobSkill(e) {
    var jobId = e.getAttribute("jobId");
    var skillId = e.getAttribute("skillId");

    fetch("/recruiter/api/jobs/skills/remove", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            jobId: jobId,
            skillId: skillId
        })
    }).then(response => {
        return response.json()
    }).then(json => {
        if (json["success"] == false) {
            alert(json["error"]);
            return;
        }
        e.parentNode.remove();
    })
}

// Functions for job detail page skill management
function addJobSkillFromDetail(jobId) {
    var skillInput = document.getElementById('newSkillInput');
    var skill = skillInput.value.trim();

    if (skill === "") {
        return;
    }

    fetch("/recruiter/api/jobs/skills/add", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            jobId: jobId,
            skill: skill
        })
    }).then(response => {
        return response.json()
    }).then(json => {
        if (json["success"] == false) {
            alert(json["error"]);
            return;
        }

        var skillsContainer = document.querySelector('.skills-container');
        var newSkillElement = document.createElement("div");
        newSkillElement.className = "skill-tag";
        newSkillElement.setAttribute("data-skill-id", json.skillId);
        newSkillElement.innerHTML = `
            <span>${skill}</span>
            <button class="remove-skill-btn" onclick="removeJobSkillFromDetail(${jobId}, ${json.skillId}, this)">×</button>
        `;
        skillsContainer.appendChild(newSkillElement);
        skillInput.value = "";
        
        // Hide "no skills" message if it exists
        var noSkillsMsg = document.querySelector('.no-skills');
        if (noSkillsMsg) {
            noSkillsMsg.style.display = 'none';
        }
    })
}

function removeJobSkillFromDetail(jobId, skillId, button) {
    fetch("/recruiter/api/jobs/skills/remove", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            jobId: jobId,
            skillId: skillId
        })
    }).then(response => {
        return response.json()
    }).then(json => {
        if (json["success"] == false) {
            alert(json["error"]);
            return;
        }
        button.parentNode.remove();
        
        // Show "no skills" message if no skills left
        var remainingSkills = document.querySelectorAll('.skill-tag');
        if (remainingSkills.length === 0) {
            var skillsContainer = document.querySelector('.skills-container');
            var noSkillsMsg = document.querySelector('.no-skills');
            if (noSkillsMsg) {
                noSkillsMsg.style.display = 'block';
            }
        }
    })
}

// Functions for edit job page skill management
function addJobSkillFromEdit(jobId) {
    var skillInput = document.getElementById('newJobSkill');
    var skill = skillInput.value.trim();

    if (skill === "") {
        return;
    }

    fetch("/recruiter/api/jobs/skills/add", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            jobId: jobId,
            skill: skill
        })
    }).then(response => {
        return response.json()
    }).then(json => {
        if (json["success"] == false) {
            alert(json["error"]);
            return;
        }

        var skillsList = document.querySelector('.skills-list');
        if (!skillsList) {
            // Create skills list if it doesn't exist
            var currentSkills = document.querySelector('.current-skills');
            var noSkillsMsg = currentSkills.querySelector('.no-skills');
            if (noSkillsMsg) {
                noSkillsMsg.remove();
            }
            
            skillsList = document.createElement('div');
            skillsList.className = 'skills-list';
            currentSkills.insertBefore(skillsList, currentSkills.querySelector('.add-skill-section'));
        }
        
        var newSkillElement = document.createElement("div");
        newSkillElement.className = "skill-item";
        newSkillElement.setAttribute("data-skill-id", json.skillId);
        newSkillElement.innerHTML = `
            <span class="skill-name">${skill}</span>
            <button type="button" class="remove-skill-btn" onclick="removeJobSkillFromEdit(${jobId}, ${json.skillId}, this)">×</button>
        `;
        skillsList.appendChild(newSkillElement);
        skillInput.value = "";
    })
}

function removeJobSkillFromEdit(jobId, skillId, button) {
    fetch("/recruiter/api/jobs/skills/remove", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            jobId: jobId,
            skillId: skillId
        })
    }).then(response => {
        return response.json()
    }).then(json => {
        if (json["success"] == false) {
            alert(json["error"]);
            return;
        }
        button.parentNode.remove();
        
        // Check if no skills left
        var remainingSkills = document.querySelectorAll('.skill-item');
        if (remainingSkills.length === 0) {
            var skillsList = document.querySelector('.skills-list');
            if (skillsList) {
                skillsList.remove();
            }
            
            // Add "no skills" message back
            var currentSkills = document.querySelector('.current-skills');
            var addSkillSection = currentSkills.querySelector('.add-skill-section');
            var noSkillsMsg = document.createElement('p');
            noSkillsMsg.className = 'no-skills';
            noSkillsMsg.textContent = 'No skills added yet.';
            currentSkills.insertBefore(noSkillsMsg, addSkillSection);
        }
    })
}

// Add event listeners for Enter key on skill inputs
document.addEventListener('DOMContentLoaded', function() {
    // For job detail page
    var newSkillInput = document.getElementById('newSkillInput');
    if (newSkillInput) {
        newSkillInput.addEventListener('keyup', function(event) {
            if (event.key === 'Enter') {
                var jobId = this.closest('[data-job-id]')?.getAttribute('data-job-id');
                if (jobId) {
                    addJobSkillFromDetail(parseInt(jobId));
                }
            }
        });
    }
    
    // For edit job page
    var newJobSkillInput = document.getElementById('newJobSkill');
    if (newJobSkillInput) {
        newJobSkillInput.addEventListener('keyup', function(event) {
            if (event.key === 'Enter') {
                var jobId = this.closest('form')?.action.match(/\/jobs\/(\d+)\/edit/)?.[1];
                if (jobId) {
                    addJobSkillFromEdit(parseInt(jobId));
                }
            }
        });
    }
});

// Function to handle viewing job applications
function viewJobApplications(jobId) {
    window.location.href = `/recruiter/jobs/${jobId}`;
}

// Function to toggle job details
function toggleJobDetails(jobId) {
    var jobContainer = document.querySelector(`[jobId="${jobId}"] .jobContainer`);
    jobContainer.classList.toggle('expanded');
}

// Auto-save functionality (optional)
function enableAutoSave() {
    var inputs = document.querySelectorAll('input, textarea');
    inputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            // Auto-save logic could be implemented here
            // For now, we'll just indicate that changes are unsaved
            var saveButton = input.closest('.jobField, #profile').querySelector('button[class*="save"]');
            if (saveButton) {
                saveButton.style.backgroundColor = '#f39c12'; // Orange to indicate unsaved changes
                saveButton.textContent = saveButton.textContent.replace('Save', 'Save*');
            }
        });
    });
}

// Initialize auto-save on page load
document.addEventListener('DOMContentLoaded', function() {
    enableAutoSave();
});

// Reset button appearance after save
function resetSaveButton(button) {
    button.style.backgroundColor = '';
    button.textContent = button.textContent.replace('*', '');
}