# Fixed insertQueries to match the updated models and schema
insertQueries = {
    # Basic entity inserts (exclude auto-generated fields)
    "Recruiters": "INSERT INTO Recruiters (username, email, password) VALUES (?, ?, ?)",
    "Freelancers": "INSERT INTO Freelancers (username, email, password) VALUES (?, ?, ?)",
    "Companies": "INSERT INTO Companies (username, companyName, companyPhone, companyAddress, companyDescription, employeeSize) VALUES (?, ?, ?, ?, ?, ?)",
    "Skills": "INSERT INTO Skills (skill) VALUES (?)",
    
    # JobPosts - exclude postedOn (auto-set)
    "JobPosts": "INSERT INTO JobPosts (recruiterId, companyId, title, description, experience, jobType, location, salary, validTill, isActive) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    
    # Experiences and Educations
    "Experiences": "INSERT INTO Experiences (freelancerId, companyName, startDate, endDate, role, description) VALUES (?, ?, ?, ?, ?, ?)",
    "Educations": "INSERT INTO Educations (freelancerId, course, degree, school, startDate, endDate, cgpa) VALUES (?, ?, ?, ?, ?, ?, ?)",
    
    # Resumes - exclude uploadedAt (auto-set)
    "Resumes": "INSERT INTO Resumes (freelancerId, name, pdfData, fileSize, isDefault) VALUES (?, ?, ?, ?, ?)",
    
    # Junction tables - exclude auto-set timestamp fields
    "PostSkills": "INSERT INTO PostSkills (postId, skillId, isRequired) VALUES (?, ?, ?)",
    "RecruiterCompanies": "INSERT INTO RecruiterCompanies (recruiterId, companyId, role, isActive) VALUES (?, ?, ?, ?)",
    "FreelancerSkills": "INSERT INTO FreelancerSkills (freelancerId, skillId, proficiencyLevel, yearsOfExperience) VALUES (?, ?, ?, ?)",
    
    # Applications - now treated as DataModel, exclude all auto-generated fields
    "Applications": "INSERT INTO Applications (jobPostId, freelancerId, status, resumeId, coverLetter) VALUES (?, ?, ?, ?, ?)"
}

createTable = {
    "Recruiters": """
    CREATE TABLE IF NOT EXISTS Recruiters (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );""",
    
    "Freelancers": """
    CREATE TABLE IF NOT EXISTS Freelancers (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );""",
    
    "FreelancerDetails": """
    CREATE TABLE IF NOT EXISTS FreelancerDetails (
        freelancerId INTEGER NOT NULL PRIMARY KEY,
        firstName VARCHAR(255),
        middleName VARCHAR(255),
        lastName VARCHAR(255),
        phoneNumber VARCHAR(20),
        contactEmail VARCHAR(255),
        about TEXT,
        dateOfBirth DATE,
        FOREIGN KEY(freelancerId) REFERENCES Freelancers(id) ON DELETE CASCADE
    );""",
    
    "Companies": """
    CREATE TABLE IF NOT EXISTS Companies (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        companyName TEXT NOT NULL,
        companyPhone TEXT NOT NULL,
        companyAddress TEXT NOT NULL,
        companyDescription TEXT NOT NULL,
        employeeSize INTEGER NOT NULL DEFAULT 1 CHECK(employeeSize > 0),
        createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );""",
    
    "Skills": """
    CREATE TABLE IF NOT EXISTS Skills (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        skill TEXT NOT NULL UNIQUE,
        createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );""",
    
    "JobPosts": """
    CREATE TABLE IF NOT EXISTS JobPosts (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        recruiterId INTEGER NOT NULL,
        companyId INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        experience INTEGER NOT NULL CHECK(experience >= 0),
        jobType TEXT NOT NULL CHECK(jobType IN ('FULL_TIME', 'PART_TIME', 'CONTRACT', 'INTERNSHIP', 'FREELANCE')),
        location TEXT NOT NULL,
        salary REAL NOT NULL CHECK(salary >= 0),
        postedOn TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        validTill TEXT NOT NULL,
        isActive BOOLEAN NOT NULL DEFAULT 1,
        createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(recruiterId) REFERENCES Recruiters(id) ON DELETE CASCADE,
        FOREIGN KEY(companyId) REFERENCES Companies(id) ON DELETE CASCADE
    );""",
    
    "PostSkills": """
    CREATE TABLE IF NOT EXISTS PostSkills (
        postId INTEGER NOT NULL,
        skillId INTEGER NOT NULL,
        isRequired BOOLEAN NOT NULL DEFAULT 1,
        createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (postId, skillId),
        FOREIGN KEY(postId) REFERENCES JobPosts(id) ON DELETE CASCADE,
        FOREIGN KEY(skillId) REFERENCES Skills(id) ON DELETE CASCADE
    );""",
    
    "RecruiterCompanies": """
    CREATE TABLE IF NOT EXISTS RecruiterCompanies (
        recruiterId INTEGER NOT NULL,
        companyId INTEGER NOT NULL,
        role TEXT NOT NULL DEFAULT "RECRUITER" CHECK(role IN ('RECRUITER', 'ADMIN', 'HR_MANAGER')),
        joinedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        isActive BOOLEAN NOT NULL DEFAULT 1,
        createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (recruiterId, companyId),
        FOREIGN KEY(recruiterId) REFERENCES Recruiters(id) ON DELETE CASCADE,
        FOREIGN KEY(companyId) REFERENCES Companies(id) ON DELETE CASCADE
    );""",
    
    "Experiences": """
    CREATE TABLE IF NOT EXISTS Experiences (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        freelancerId INTEGER NOT NULL,
        companyName TEXT NOT NULL,
        startDate TEXT NOT NULL,
        endDate TEXT,
        role TEXT NOT NULL,
        description TEXT,
        createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(freelancerId) REFERENCES Freelancers(id) ON DELETE CASCADE,
        CHECK(endDate IS NULL OR endDate >= startDate)
    );""",
    
    "Educations": """
    CREATE TABLE IF NOT EXISTS Educations (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        freelancerId INTEGER NOT NULL,
        course TEXT NOT NULL,
        degree TEXT NOT NULL,
        school TEXT NOT NULL,
        startDate TEXT NOT NULL,
        endDate TEXT NOT NULL,
        cgpa REAL NOT NULL CHECK(cgpa >= 0.0 AND cgpa <= 10.0),
        createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(freelancerId) REFERENCES Freelancers(id) ON DELETE CASCADE,
        CHECK(endDate >= startDate)
    );""",
    
    "FreelancerSkills": """
    CREATE TABLE IF NOT EXISTS FreelancerSkills (
        freelancerId INTEGER NOT NULL,
        skillId INTEGER NOT NULL,
        proficiencyLevel TEXT NOT NULL DEFAULT "BEGINNER" CHECK(proficiencyLevel IN ('BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT')),
        yearsOfExperience INTEGER DEFAULT 0 CHECK(yearsOfExperience >= 0),
        createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (freelancerId, skillId),
        FOREIGN KEY(freelancerId) REFERENCES Freelancers(id) ON DELETE CASCADE,
        FOREIGN KEY(skillId) REFERENCES Skills(id) ON DELETE CASCADE
    );""",
    
    "Resumes": """
    CREATE TABLE IF NOT EXISTS Resumes (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        freelancerId INTEGER NOT NULL,
        name TEXT NOT NULL,
        pdfData BLOB NOT NULL,
        fileSize INTEGER NOT NULL CHECK(fileSize > 0),
        isDefault BOOLEAN NOT NULL DEFAULT 0,
        uploadedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(freelancerId) REFERENCES Freelancers(id) ON DELETE CASCADE
    );""",
    
    "Applications": """
    CREATE TABLE IF NOT EXISTS Applications (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        jobPostId INTEGER NOT NULL,
        freelancerId INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT "PENDING" CHECK(status IN ('PENDING', 'UNDER_REVIEW', 'SHORTLISTED', 'INTERVIEWED', 'ACCEPTED', 'REJECTED', 'WITHDRAWN')),
        appliedOn TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        resumeId INTEGER NOT NULL,
        coverLetter TEXT,
        createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(jobPostId, freelancerId),
        FOREIGN KEY(jobPostId) REFERENCES JobPosts(id) ON DELETE CASCADE,
        FOREIGN KEY(freelancerId) REFERENCES Freelancers(id) ON DELETE CASCADE,
        FOREIGN KEY(resumeId) REFERENCES Resumes(id) ON DELETE RESTRICT
    );"""
}

# Updated indexes to match PascalCase table names
createIndexes = {
    "idx_recruiters_email": "CREATE INDEX IF NOT EXISTS idx_recruiters_email ON Recruiters(email);",
    "idx_recruiters_username": "CREATE INDEX IF NOT EXISTS idx_recruiters_username ON Recruiters(username);",
    "idx_freelancers_email": "CREATE INDEX IF NOT EXISTS idx_freelancers_email ON Freelancers(email);",
    "idx_freelancers_username": "CREATE INDEX IF NOT EXISTS idx_freelancers_username ON Freelancers(username);",
    "idx_companies_username": "CREATE INDEX IF NOT EXISTS idx_companies_username ON Companies(username);",
    "idx_jobposts_company": "CREATE INDEX IF NOT EXISTS idx_jobposts_company ON JobPosts(companyId);",
    "idx_jobposts_recruiter": "CREATE INDEX IF NOT EXISTS idx_jobposts_recruiter ON JobPosts(recruiterId);",
    "idx_jobposts_active": "CREATE INDEX IF NOT EXISTS idx_jobposts_active ON JobPosts(isActive, postedOn);",
    "idx_applications_freelancer": "CREATE INDEX IF NOT EXISTS idx_applications_freelancer ON Applications(freelancerId);",
    "idx_applications_status": "CREATE INDEX IF NOT EXISTS idx_applications_status ON Applications(status);",
    "idx_applications_jobpost": "CREATE INDEX IF NOT EXISTS idx_applications_jobpost ON Applications(jobPostId);",
    "idx_experiences_freelancer": "CREATE INDEX IF NOT EXISTS idx_experiences_freelancer ON Experiences(freelancerId);",
    "idx_educations_freelancer": "CREATE INDEX IF NOT EXISTS idx_educations_freelancer ON Educations(freelancerId);",
    "idx_resumes_freelancer": "CREATE INDEX IF NOT EXISTS idx_resumes_freelancer ON Resumes(freelancerId);",
    "idx_resumes_default": "CREATE INDEX IF NOT EXISTS idx_resumes_default ON Resumes(freelancerId, isDefault);",
    "idx_postskills_post": "CREATE INDEX IF NOT EXISTS idx_postskills_post ON PostSkills(postId);",
    "idx_postskills_skill": "CREATE INDEX IF NOT EXISTS idx_postskills_skill ON PostSkills(skillId);",
    "idx_recruitercompanies_recruiter": "CREATE INDEX IF NOT EXISTS idx_recruitercompanies_recruiter ON RecruiterCompanies(recruiterId);",
    "idx_recruitercompanies_company": "CREATE INDEX IF NOT EXISTS idx_recruitercompanies_company ON RecruiterCompanies(companyId);",
    "idx_freelancerskills_freelancer": "CREATE INDEX IF NOT EXISTS idx_freelancerskills_freelancer ON FreelancerSkills(freelancerId);",
    "idx_freelancerskills_skill": "CREATE INDEX IF NOT EXISTS idx_freelancerskills_skill ON FreelancerSkills(skillId);"
}