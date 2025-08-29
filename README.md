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
CREATE TABLE recruiters (
    id INTEGER PRIMARY KEY AUTO INCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);


```