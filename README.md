# SkillConnect
Freelance Market Place


## Modules
Modules to be Implemented:
- User Authentication & Profile Setup Module
- Job Posting & Application System Module
- Recruiter Dashboard & Notification System Module
- Testing, Review, and Documentation

There are two types of users. One is recruiter and the other is Freelancer. Each recruiter represent a company, and each recruiter can post jobs for a specific company.

## My thoughts
- What if two recruiters represent a same company?
- What if a recruiter wants to represent two different comapny?
* So, the recruiters and company should have different tables, and the are joined using another table thus froming a many to many relation. Hence, n number of recruiter can represent m number of companies.

- How is the post related to the company and the recruiter?
* The post will be created, and then a new table mapping company id, post id and recruiter id will be created. This way it would be easier to map the recruiter, company and post.
* also, verify that the recruiter id is actually related to that company id in the many to many relation.
* there should be an admins for the companies, to maintain proper conduct

- Lets think about freelancer.
* the will login, create a complete profile, add skills, educations, experience, and so on.
* they should be able to search jobs, and should also get job recommendations based on their profile.

- How does freelancer applying to a job work?
* freelancer sees a post, and clicks apply. Now, in the Applications table, the postId and the freelancerId are stored, along with status (applied, seen, accepted, declined).

## sum up of thoughts
freelancer and recruiter have seperate tables to store their primary details.
Tables: freelancers, recruiters

freelancer has a to create profile
Tables: experiences, educations, freelancerSkills
To store skills:
Tables: skills
the freelancer profile is done.

recruiter has to create companies.
Tables: companies, recruiterCompanies
the companies work is done.

The recruiter has to post jobs
Tables: jobPosts, recruiterCompanyPosts
the posts are done.

The freelancer has to apply to the post
Tables: applications
application process is also done.

## Schema of these tables:
```sql
-- Recruiters Table
CREATE TABLE IF NOT EXISTS recruiters (
    id INTEGER PRIMARY KEY AUTO INCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Company Table
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTO INCREMENT,
    username TEXT UNIQUE NOT NULL,
    companyName TEXT NOT NULL,
    companyPhone TEXT NOT NULL,
    companyAddress TEXT NOT NULL,
    companyDescription TEXT NOT NULL,
    employeeSize INTEGER NOT NULL DEFAULT 1
);

-- RecruiterCompanies Table
CREATE TABLE IF NOT EXISTS recruiterCompanies (
    recruiterId INTEGER NOT NULL,
    companyId INTEGER NOT NULL,
    role TEXT NOT NULL DEFAULT "RECRUITER" CHECK role IN ('RECRUITER', 'ADMIN'),
    PRIMARY KEY (recruiterId, companyId),
    FOREIGN KEY (recruiterId) REFERENCES recruiters(id) ON CASCADE DELETE,
    FOREIGN KEY (companyId) REFERENCES companies(id) ON CASCADE DELETE
);

-- Job Posts
CREATE TABLE IF NOT EXISTS jobPosts (
    id INTEGER PRIMARY KEY AUTO INCREMENT,
    jobTitle TEXT,
    jobDescription TEXT,
    experienceRequired INTEGER,
    jobType TEXT CHECK jobType IN ('FULL-TIME', 'PART-TIME', 'INTERN', 'TRAINING')
);

-- Skills Table
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTO INCREMENT,
    skill TEXT UNIQUE NOT NULL
);

-- jobPost to Skills
CREATE TABLE IF NOT EXISTS postSkills (
    postId INTEGER NOT NULL,
    skillId INTEGER NOT NULL,
    PRIMARY KEY (postId, skillId),
    FOREIGN KEY postId REFERENCES post(id) ON CASCADE DELETE,
    FOREIGN KEY skillId REFERENCES skills(id) ON CASCADE DELETE
)

-- Recruiter Company Posts
CREATE TABLE IF NOT EXISTS recruiterCompanyPosts (
    recruiterId INTEGER NOT NULL,
    companyId INTEGER NOT NULL,
    postId INTEGER NOT NULL,
    PRIMARY KEY (recruiterId, companyId, postId),
    FOREIGN KEY (recruiterId) REFERENCES recruiters(id) ON CASCADE DELETE,
    FOREIGN KEY (companyId) REFERENCES companies(id) ON CASCADE DELETE,
    FOREIGN KEY (postId) REFERENCES jonPosts(id) ON CASCADE DELETE
)


-- Freelancers Table
CREATE TABLE IF NOT EXISTS freelancers (
    id INTEGER PRIMARY KEY AUTO INCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Freelancer Details
CREATE TABLE IF NOT EXISTS freelancerDetails (
    freelancerId INTEGER UNIQUE NOT NULL,
    firstName VARCHAR(255),
    middleName VARCHAR(255),
    lastName VARCHAR(255),
    phoneNumber VARCHAR(20),
    contactEmail VARCHAR(255),
    about TEXT,
    dateOfBirth DATE,
)

-- Freelancer Educations
CREATE TABLE IF NOT EXISTS educations (
    id INTEGER PRIMARY KEY AUTO INCREMENT,
    freelancerId INTEGER NOT NULL,
    course TEXT,
    degree TEXT,
    school TEXT,
    startDate DATE,
    endDate DATE CHECK (startDate <= endDate),
    cgpa DOUBLE,
    FOREIGN KEY freelancerId REFERENCES freelancers(id) ON CASCADE DELETE
);

-- Freelancer Experiences
CREATE TABLE IF NOT EXISTS experiences (
    id INTEGER PRIMARY KEY AUTO INCREMENT,
    freelancerId INTEGER NOT NULL,
    companyName TEXT,
    startDate DATE,
    endDate DATE CHECK (startDate <= endDate),
    role VARCHAR(255),
    FOREIGN KEY freelancerId REFERENCES freelancers(id) ON CASCADE DELETE
);

-- Freelancers to Skills
CREATE TABLE IF NOT EXISTS freelancerSkills (
    freelancerId INTEGER NOT NULL,
    skillId INTEGER NOT NULL,
    PRIMARY KEY (freelancerId, skillId),
    FOREIGN KEY freelancerId REFERENCES freelancers(id) ON CASCADE DELETE,
    FOREIGN KEY skillId REFERENCES skills(id) ON CASCADE DELETE
);

-- Applications Table
CREATE TABLE IF NOT EXISTS applications (
    postId INTEGER NOT NULL,
    freelancerId INTEGER NOT NULL,
    status TEXT CHECK status IN ('APPLIED', 'SEEN', 'ACCEPTED', 'REJECTED'),
    appliedOn DATE,
    PRIMARY KEY (postId, freelancerId),
    FOREIGN KEY (postId) REFERENCES jobPosts(id) ON CASCADE DELETE,
    FOREIGN KEY (freelancerId) REFERENCES freelancers(id) ON CASCADE DELETE
);
```