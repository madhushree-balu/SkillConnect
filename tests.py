import unittest
import sqlite3
import os
import tempfile
from datetime import datetime, timedelta
from models import *
from database_setup import create_database, drop_all_tables


class TestDatabaseSetup(unittest.TestCase):
    """Test database setup and teardown"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database"""
        # Use a temporary database for testing
        cls.test_db = "test_database.db"
        # Backup original database connection if it exists
        if os.path.exists("database.db"):
            os.rename("database.db", "database_backup.db")
        
        # Create test database
        os.rename(cls.test_db, "database.db") if os.path.exists(cls.test_db) else None
        create_database()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database"""
        # Remove test database
        if os.path.exists("database.db"):
            os.remove("database.db")
        
        # Restore original database if it existed
        if os.path.exists("database_backup.db"):
            os.rename("database_backup.db", "database.db")
    
    def setUp(self):
        """Clear all data before each test and enable foreign keys"""
        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            
            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Clear all tables in proper order
            tables = ["Applications", "FreelancerSkills", "RecruiterCompanies", 
                     "PostSkills", "Resumes", "Educations", "Experiences", 
                     "JobPosts", "Skills", "Companies", "Freelancers", "Recruiters"]
            
            for table in tables:
                cursor.execute(f"DELETE FROM {table}")
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Setup error: {e}")


class TestDataModels(TestDatabaseSetup):
    """Test all DataModel classes"""
    
    def test_recruiters_crud(self):
        """Test Recruiters CRUD operations"""
        # Test insert
        recruiter = Recruiters(
            username="test_recruiter",
            email="recruiter@test.com", 
            password="password123"
        )
        
        recruiter_id = recruiter.insert()
        self.assertIsNotNone(recruiter_id)
        
        # Test get by id
        retrieved = Recruiters.get(id=recruiter_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.username, "test_recruiter")
        self.assertEqual(retrieved.email, "recruiter@test.com")
        
        # Test get by email
        retrieved_by_email = Recruiters.get(email="recruiter@test.com")
        self.assertIsNotNone(retrieved_by_email)
        self.assertEqual(retrieved_by_email.id, recruiter_id)
        
        # Test update
        retrieved.username = "updated_recruiter"
        result = retrieved.update()
        self.assertIsNotNone(result)
        
        updated = Recruiters.get(id=recruiter_id)
        self.assertEqual(updated.username, "updated_recruiter")
        
        # Test getAll
        all_recruiters = Recruiters.getAll()
        self.assertEqual(len(all_recruiters), 1)
        
        # Test delete
        result = retrieved.delete()
        self.assertIsNotNone(result)
        
        deleted = Recruiters.get(id=recruiter_id)
        self.assertIsNone(deleted)
    
    def test_freelancers_crud(self):
        """Test Freelancers CRUD operations"""
        freelancer = Freelancers(
            username="test_freelancer",
            email="freelancer@test.com",
            password="password123"
        )
        
        freelancer_id = freelancer.insert()
        self.assertIsNotNone(freelancer_id)
        
        # Test retrieval
        retrieved = Freelancers.get(id=freelancer_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.username, "test_freelancer")
        
        # Test unique constraint (should fail)
        duplicate = Freelancers(
            username="test_freelancer",  # Same username
            email="different@test.com",
            password="password123"
        )
        
        duplicate_id = duplicate.insert()
        self.assertIsNone(duplicate_id)  # Should fail due to unique constraint
    
    def test_companies_crud(self):
        """Test Companies CRUD operations"""
        company = Companies(
            username="test_company",
            companyName="Test Corp",
            companyPhone="+1234567890",
            companyAddress="123 Test St",
            companyDescription="A test company",
            employeeSize=50
        )
        
        company_id = company.insert()
        self.assertIsNotNone(company_id)
        
        retrieved = Companies.get(id=company_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.companyName, "Test Corp")
        self.assertEqual(retrieved.employeeSize, 50)
    
    def test_skills_crud(self):
        """Test Skills CRUD operations"""
        skill = Skills(skill="Python")
        skill_id = skill.insert()
        self.assertIsNotNone(skill_id)
        
        retrieved = Skills.get(id=skill_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.skill, "Python")
        
        # Test unique constraint
        duplicate_skill = Skills(skill="Python")
        duplicate_id = duplicate_skill.insert()
        self.assertIsNone(duplicate_id)
    
    def test_job_posts_crud(self):
        """Test JobPosts CRUD operations with foreign keys"""
        # First create dependencies
        recruiter = Recruiters(username="recruiter1", email="r1@test.com", password="pass")
        recruiter_id = recruiter.insert()
        
        company = Companies(
            username="company1", companyName="Tech Corp", companyPhone="123456789",
            companyAddress="Tech St", companyDescription="Tech company", employeeSize=100
        )
        company_id = company.insert()
        
        # Create job post
        job_post = JobPosts(
            recruiterId=recruiter_id,
            companyId=company_id,
            title="Python Developer",
            description="Looking for Python developer",
            experience=2,
            jobType="FULL_TIME",
            location="Remote",
            salary=75000.0,
            validTill="2025-12-31",
            isActive=True
        )
        
        job_id = job_post.insert()
        self.assertIsNotNone(job_id)
        
        retrieved = JobPosts.get(id=job_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.title, "Python Developer")
        self.assertEqual(retrieved.salary, 75000.0)
        self.assertIsNotNone(retrieved.postedOn)  # Should be auto-set
    
    def test_experiences_crud(self):
        """Test Experiences CRUD operations"""
        # Create freelancer first
        freelancer = Freelancers(username="freelancer1", email="f1@test.com", password="pass")
        freelancer_id = freelancer.insert()
        
        # Test current position (no end date)
        current_exp = Experiences(
            freelancerId=freelancer_id,
            companyName="Current Corp",
            startDate="2024-01-01",
            endDate=None,  # Current position
            role="Software Developer",
            description="Current role"
        )
        
        exp_id = current_exp.insert()
        self.assertIsNotNone(exp_id)
        
        retrieved = Experiences.get(id=exp_id)
        self.assertIsNotNone(retrieved)
        self.assertIsNone(retrieved.endDate)
        
        # Test past position
        past_exp = Experiences(
            freelancerId=freelancer_id,
            companyName="Previous Corp",
            startDate="2022-01-01",
            endDate="2023-12-31",
            role="Junior Developer",
            description="Previous role"
        )
        
        past_id = past_exp.insert()
        self.assertIsNotNone(past_id)
        
        # Test getAll for freelancer
        all_exp = Experiences.getAll(freelancerId=freelancer_id)
        self.assertEqual(len(all_exp), 2)
    
    def test_educations_crud(self):
        """Test Educations CRUD operations"""
        freelancer = Freelancers(username="freelancer2", email="f2@test.com", password="pass")
        freelancer_id = freelancer.insert()
        
        education = Educations(
            freelancerId=freelancer_id,
            course="Computer Science",
            degree="Bachelor's",
            school="Test University",
            startDate="2020-09-01",
            endDate="2024-05-01",
            cgpa=8.5
        )
        
        edu_id = education.insert()
        self.assertIsNotNone(edu_id)
        
        retrieved = Educations.get(id=edu_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.cgpa, 8.5)
    
    def test_resumes_crud(self):
        """Test Resumes CRUD operations"""
        freelancer = Freelancers(username="freelancer3", email="f3@test.com", password="pass")
        freelancer_id = freelancer.insert()
        
        # Test PDF data (using dummy bytes)
        pdf_data = b"dummy pdf content for testing"
        
        resume = Resumes(
            freelancerId=freelancer_id,
            name="John_Doe_Resume.pdf",
            pdfData=pdf_data,
            fileSize=len(pdf_data),
            isDefault=True
        )
        
        resume_id = resume.insert()
        self.assertIsNotNone(resume_id)
        
        retrieved = Resumes.get(id=resume_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "John_Doe_Resume.pdf")
        self.assertEqual(retrieved.fileSize, len(pdf_data))
        self.assertTrue(retrieved.isDefault)
        self.assertIsNotNone(retrieved.uploadedAt)  # Should be auto-set


class TestJunctionModels(TestDatabaseSetup):
    """Test all JunctionModel classes"""
    
    def setUp(self):
        """Set up test data for junction models"""
        super().setUp()
        
        # Create test entities
        self.recruiter = Recruiters(username="recruiter1", email="r1@test.com", password="pass")
        self.recruiter_id = self.recruiter.insert()
        
        self.company = Companies(
            username="company1", companyName="Tech Corp", companyPhone="123456789",
            companyAddress="Tech St", companyDescription="Tech company", employeeSize=100
        )
        self.company_id = self.company.insert()
        
        self.freelancer = Freelancers(username="freelancer1", email="f1@test.com", password="pass")
        self.freelancer_id = self.freelancer.insert()
        
        self.skill = Skills(skill="Python")
        self.skill_id = self.skill.insert()
        
        self.job_post = JobPosts(
            recruiterId=self.recruiter_id,
            companyId=self.company_id,
            title="Developer",
            description="Job description",
            experience=2,
            jobType="FULL_TIME",
            location="Remote",
            salary=75000.0,
            validTill="2025-12-31"
        )
        self.job_id = self.job_post.insert()
        
        # Create resume for applications
        pdf_data = b"dummy pdf content"
        self.resume = Resumes(
            freelancerId=self.freelancer_id,
            name="test_resume.pdf",
            pdfData=pdf_data,
            fileSize=len(pdf_data),
            isDefault=True
        )
        self.resume_id = self.resume.insert()
    
    def test_post_skills(self):
        """Test PostSkills junction model"""
        post_skill = PostSkills(
            postId=self.job_id,
            skillId=self.skill_id,
            isRequired=True
        )
        
        result = post_skill.insert()
        self.assertIsNotNone(result)
        
        # Test retrieval
        retrieved = PostSkills.get(postId=self.job_id, skillId=self.skill_id)
        self.assertIsNotNone(retrieved)
        self.assertTrue(retrieved.isRequired)
        
        # Test getAll
        all_post_skills = PostSkills.getAll(postId=self.job_id)
        self.assertEqual(len(all_post_skills), 1)
        
        # Test delete
        result = retrieved.delete()
        self.assertIsNotNone(result)
        
        deleted = PostSkills.get(postId=self.job_id, skillId=self.skill_id)
        self.assertIsNone(deleted)
    
    def test_recruiter_companies(self):
        """Test RecruiterCompanies junction model"""
        recruiter_company = RecruiterCompanies(
            recruiterId=self.recruiter_id,
            companyId=self.company_id,
            role="ADMIN",
            isActive=True
        )
        
        result = recruiter_company.insert()
        self.assertIsNotNone(result)
        
        retrieved = RecruiterCompanies.get(recruiterId=self.recruiter_id, companyId=self.company_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.role, "ADMIN")
        self.assertIsNotNone(retrieved.joinedAt)  # Should be auto-set
        
        # Test update
        new_values = {"role": "HR_MANAGER"}
        where_conditions = {"recruiterId": self.recruiter_id, "companyId": self.company_id}
        result = retrieved.update(new_values, where_conditions)
        self.assertIsNotNone(result)
        
        updated = RecruiterCompanies.get(recruiterId=self.recruiter_id, companyId=self.company_id)
        self.assertEqual(updated.role, "HR_MANAGER")
    
    def test_freelancer_skills(self):
        """Test FreelancerSkills junction model"""
        freelancer_skill = FreelancerSkills(
            freelancerId=self.freelancer_id,
            skillId=self.skill_id,
            proficiencyLevel="INTERMEDIATE",
            yearsOfExperience=3
        )
        
        result = freelancer_skill.insert()
        self.assertIsNotNone(result)
        
        retrieved = FreelancerSkills.get(freelancerId=self.freelancer_id, skillId=self.skill_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.proficiencyLevel, "INTERMEDIATE")
        self.assertEqual(retrieved.yearsOfExperience, 3)
    
    def test_applications(self):
        """Test Applications model (now DataModel)"""
        application = Applications(
            jobPostId=self.job_id,
            freelancerId=self.freelancer_id,
            status="PENDING",
            resumeId=self.resume_id,
            coverLetter="I am interested in this position."
        )
        
        app_id = application.insert()
        self.assertIsNotNone(app_id)
        
        retrieved = Applications.get(id=app_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.status, "PENDING")
        self.assertEqual(retrieved.jobPostId, self.job_id)
        self.assertEqual(retrieved.freelancerId, self.freelancer_id)
        self.assertIsNotNone(retrieved.appliedOn)  # Should be auto-set
        
        # Test status update
        retrieved.status = "UNDER_REVIEW"
        result = retrieved.update(status="UNDER_REVIEW")
        self.assertIsNotNone(result)
        
        updated = Applications.get(id=app_id)
        self.assertEqual(updated.status, "UNDER_REVIEW")


class TestModelValidation(TestDatabaseSetup):
    """Test model validation and constraints"""
    
    def test_unique_constraints(self):
        """Test unique constraint violations"""
        # Test recruiter email uniqueness
        recruiter1 = Recruiters(username="rec1", email="same@test.com", password="pass")
        recruiter2 = Recruiters(username="rec2", email="same@test.com", password="pass")
        
        id1 = recruiter1.insert()
        id2 = recruiter2.insert()
        
        self.assertIsNotNone(id1)
        self.assertIsNone(id2)  # Should fail due to unique email
        
        # Test skill uniqueness
        skill1 = Skills(skill="JavaScript")
        skill2 = Skills(skill="JavaScript")
        
        skill_id1 = skill1.insert()
        skill_id2 = skill2.insert()
        
        self.assertIsNotNone(skill_id1)
        self.assertIsNone(skill_id2)  # Should fail due to unique skill name
    
    def test_foreign_key_constraints(self):
        """Test foreign key constraint violations"""
        # Try to create job post with non-existent recruiter
        invalid_job = JobPosts(
            recruiterId=99999,  # Non-existent
            companyId=99999,    # Non-existent
            title="Invalid Job",
            description="This should fail",
            experience=1,
            jobType="FULL_TIME",
            location="Nowhere",
            salary=50000.0,
            validTill="2025-12-31"
        )
        
        result = invalid_job.insert()
        self.assertIsNone(result)  # Should fail due to foreign key constraint
    
    def test_check_constraints(self):
        """Test check constraint violations"""
        # Test negative salary
        recruiter = Recruiters(username="rec1", email="r1@test.com", password="pass")
        recruiter_id = recruiter.insert()
        
        company = Companies(
            username="comp1", companyName="Corp", companyPhone="123",
            companyAddress="St", companyDescription="Desc", employeeSize=10
        )
        company_id = company.insert()
        
        invalid_job = JobPosts(
            recruiterId=recruiter_id,
            companyId=company_id,
            title="Invalid Job",
            description="Job with negative salary",
            experience=1,
            jobType="FULL_TIME",
            location="Remote",
            salary=-1000.0,  # Negative salary
            validTill="2025-12-31"
        )
        
        result = invalid_job.insert()
        self.assertIsNone(result)  # Should fail due to check constraint


class TestComplexQueries(TestDatabaseSetup):
    """Test complex queries and relationships"""
    
    def setUp(self):
        """Set up complex test data"""
        super().setUp()
        
        # Create test entities
        self.recruiter = Recruiters(username="recruiter1", email="r1@test.com", password="pass")
        self.recruiter_id = self.recruiter.insert()
        
        self.company = Companies(
            username="company1", companyName="Tech Corp", companyPhone="123456789",
            companyAddress="Tech St", companyDescription="Tech company", employeeSize=100
        )
        self.company_id = self.company.insert()
        
        self.freelancer1 = Freelancers(username="freelancer1", email="f1@test.com", password="pass")
        self.freelancer1_id = self.freelancer1.insert()
        
        self.freelancer2 = Freelancers(username="freelancer2", email="f2@test.com", password="pass")
        self.freelancer2_id = self.freelancer2.insert()
        
        # Create skills
        self.python_skill = Skills(skill="Python")
        self.python_id = self.python_skill.insert()
        
        self.js_skill = Skills(skill="JavaScript")
        self.js_id = self.js_skill.insert()
    
    def test_multiple_applications_same_job(self):
        """Test multiple freelancers applying to same job"""
        # Create job post
        job_post = JobPosts(
            recruiterId=self.recruiter_id,
            companyId=self.company_id,
            title="Full Stack Developer",
            description="Full stack position",
            experience=3,
            jobType="FULL_TIME",
            location="Remote",
            salary=80000.0,
            validTill="2025-12-31"
        )
        job_id = job_post.insert()
        
        # Create resumes for both freelancers
        pdf_data = b"dummy pdf content"
        
        resume1 = Resumes(
            freelancerId=self.freelancer1_id,
            name="freelancer1_resume.pdf",
            pdfData=pdf_data,
            fileSize=len(pdf_data)
        )
        resume1_id = resume1.insert()
        
        resume2 = Resumes(
            freelancerId=self.freelancer2_id,
            name="freelancer2_resume.pdf", 
            pdfData=pdf_data,
            fileSize=len(pdf_data)
        )
        resume2_id = resume2.insert()
        
        # Both freelancers apply
        app1 = Applications(
            jobPostId=job_id,
            freelancerId=self.freelancer1_id,
            resumeId=resume1_id,
            coverLetter="Application from freelancer 1"
        )
        
        app2 = Applications(
            jobPostId=job_id,
            freelancerId=self.freelancer2_id,
            resumeId=resume2_id,
            coverLetter="Application from freelancer 2"
        )
        
        app1_id = app1.insert()
        app2_id = app2.insert()
        
        self.assertIsNotNone(app1_id)
        self.assertIsNotNone(app2_id)
        
        # Test getting all applications for job
        all_apps = Applications.getAll(jobPostId=job_id)
        self.assertEqual(len(all_apps), 2)
        
        # Test duplicate application (should fail due to unique constraint)
        duplicate_app = Applications(
            jobPostId=job_id,
            freelancerId=self.freelancer1_id,  # Same freelancer, same job
            resumeId=resume1_id
        )
        
        duplicate_id = duplicate_app.insert()
        self.assertIsNone(duplicate_id)  # Should fail
    
    def test_freelancer_skills_assignment(self):
        """Test assigning multiple skills to freelancer"""
        # Assign Python skill
        python_skill_assignment = FreelancerSkills(
            freelancerId=self.freelancer1_id,
            skillId=self.python_id,
            proficiencyLevel="ADVANCED",
            yearsOfExperience=5
        )
        
        # Assign JavaScript skill
        js_skill_assignment = FreelancerSkills(
            freelancerId=self.freelancer1_id,
            skillId=self.js_id,
            proficiencyLevel="INTERMEDIATE",
            yearsOfExperience=3
        )
        
        result1 = python_skill_assignment.insert()
        result2 = js_skill_assignment.insert()
        
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        
        # Test getting all skills for freelancer
        all_skills = FreelancerSkills.getAll(freelancerId=self.freelancer1_id)
        self.assertEqual(len(all_skills), 2)
        
        # Verify skill levels
        python_assignment = FreelancerSkills.get(freelancerId=self.freelancer1_id, skillId=self.python_id)
        self.assertEqual(python_assignment.proficiencyLevel, "ADVANCED")
        self.assertEqual(python_assignment.yearsOfExperience, 5)


class TestEdgeCases(TestDatabaseSetup):
    """Test edge cases and error handling"""
    
    def test_empty_queries(self):
        """Test behavior with empty parameters"""
        # Test get with no parameters
        result = Recruiters.get()
        self.assertIsNone(result)
        
        # Test getAll with no parameters
        all_recruiters = Recruiters.getAll()
        self.assertEqual(len(all_recruiters), 0)  # Empty database
    
    def test_nonexistent_records(self):
        """Test queries for non-existent records"""
        result = Recruiters.get(id=99999)
        self.assertIsNone(result)
        
        result = Recruiters.get(email="nonexistent@test.com")
        self.assertIsNone(result)
    
    def test_tablename_property(self):
        """Test tableName property consistency"""
        self.assertEqual(Recruiters().tableName, "Recruiters")
        self.assertEqual(JobPosts().tableName, "JobPosts")
        self.assertEqual(PostSkills().tableName, "PostSkills")
        self.assertEqual(FreelancerSkills().tableName, "FreelancerSkills")
    
    def test_model_dumps(self):
        """Test model serialization"""
        recruiter = Recruiters(
            username="test",
            email="test@test.com",
            password="pass"
        )
        
        data = recruiter.model_dump()
        self.assertIn('username', data)
        self.assertIn('email', data)
        self.assertIn('password', data)
        self.assertIn('id', data)
        self.assertIn('createdAt', data)
        self.assertIn('updatedAt', data)
        
        # Test exclusions
        filtered_data = recruiter.model_dump(exclude={"id", "createdAt", "updatedAt"})
        self.assertNotIn('id', filtered_data)
        self.assertNotIn('createdAt', filtered_data)
        self.assertNotIn('updatedAt', filtered_data)


class TestDatabaseFunctions(TestDatabaseSetup):
    """Test helper database functions"""
    
    def test_execute_function(self):
        """Test execute function with valid and invalid queries"""
        # Test valid insert
        result = execute(
            "INSERT INTO Recruiters (username, email, password) VALUES (?, ?, ?)",
            ("test_user", "test@test.com", "password")
        )
        self.assertIsNotNone(result)
        
        # Test invalid query
        result = execute(
            "INSERT INTO NonExistentTable (field) VALUES (?)",
            ("value",)
        )
        self.assertIsNone(result)
    
    def test_fetch_function(self):
        """Test fetch function"""
        # Insert test data
        execute(
            "INSERT INTO Recruiters (username, email, password) VALUES (?, ?, ?)",
            ("test_user", "test@test.com", "password")
        )
        
        # Test fetch one
        result = fetch(
            "SELECT * FROM Recruiters WHERE username = ?",
            ("test_user",),
            one=True
        )
        self.assertIsNotNone(result)
        self.assertEqual(result['username'], "test_user")
        
        # Test fetch all
        results = fetch(
            "SELECT * FROM Recruiters WHERE username = ?",
            ("test_user",),
            one=False
        )
        self.assertEqual(len(results), 1)


class TestDataIntegrity(TestDatabaseSetup):
    """Test data integrity and business logic"""
    
    def test_cascade_deletes(self):
        """Test cascade delete behavior"""
        # Create recruiter and company
        recruiter = Recruiters(username="recruiter1", email="r1@test.com", password="pass")
        recruiter_id = recruiter.insert()
        
        company = Companies(
            username="company1", companyName="Corp", companyPhone="123",
            companyAddress="St", companyDescription="Desc", employeeSize=10
        )
        company_id = company.insert()
        
        # Create job post
        job_post = JobPosts(
            recruiterId=recruiter_id,
            companyId=company_id,
            title="Test Job",
            description="Test",
            experience=1,
            jobType="FULL_TIME",
            location="Remote",
            salary=50000.0,
            validTill="2025-12-31"
        )
        job_id = job_post.insert()
        
        # Verify job post exists
        retrieved_job = JobPosts.get(id=job_id)
        self.assertIsNotNone(retrieved_job)
        
        # Delete recruiter (should cascade to job post)
        retrieved_recruiter = Recruiters.get(id=recruiter_id)
        retrieved_recruiter.delete()
        
        # Job post should be deleted due to cascade
        deleted_job = JobPosts.get(id=job_id)
        self.assertIsNone(deleted_job)
    
    def test_default_values(self):
        """Test default values are applied correctly"""
        # Test company with default employee size
        company = Companies(
            username="small_company",
            companyName="Small Corp",
            companyPhone="123456789",
            companyAddress="Small St",
            companyDescription="Small company"
            # employeeSize not specified, should default to 1
        )
        
        company_id = company.insert()
        retrieved = Companies.get(id=company_id)
        self.assertEqual(retrieved.employeeSize, 1)
        
        # Test job post with default isActive
        recruiter = Recruiters(username="recruiter1", email="r1@test.com", password="pass")
        recruiter_id = recruiter.insert()
        
        job_post = JobPosts(
            recruiterId=recruiter_id,
            companyId=company_id,
            title="Test Job",
            description="Test",
            experience=1,
            jobType="FULL_TIME",
            location="Remote",
            salary=50000.0,
            validTill="2025-12-31"
            # isActive not specified, should default to True
        )
        
        job_id = job_post.insert()
        retrieved_job = JobPosts.get(id=job_id)
        self.assertTrue(retrieved_job.isActive)


def run_all_tests():
    """Run all tests and display results"""
    print("🧪 Running comprehensive model tests...\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestDataModels,
        TestJunctionModels,
        TestModelValidation,
        TestDatabaseFunctions,
        TestDataIntegrity
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip() if 'AssertionError:' in traceback else 'See details above'}")
    
    if result.errors:
        print(f"\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip() if 'Exception:' in traceback else 'See details above'}")
    
    if result.wasSuccessful():
        print(f"\n✅ All tests passed! Your models are working correctly.")
    else:
        print(f"\n⚠️  Some tests failed. Check the output above for details.")
    
    return result.wasSuccessful()


def run_specific_test(test_class_name, test_method_name=None):
    """Run a specific test class or method"""
    test_classes = {
        'TestDataModels': TestDataModels,
        'TestJunctionModels': TestJunctionModels,
        'TestModelValidation': TestModelValidation,
        'TestDatabaseFunctions': TestDatabaseFunctions,
        'TestDataIntegrity': TestDataIntegrity
    }
    
    if test_class_name not in test_classes:
        print(f"❌ Test class '{test_class_name}' not found.")
        print(f"Available classes: {', '.join(test_classes.keys())}")
        return False
    
    loader = unittest.TestLoader()
    
    if test_method_name:
        # Run specific test method
        suite = unittest.TestSuite()
        test_class = test_classes[test_class_name]
        test = test_class(test_method_name)
        suite.addTest(test)
        print(f"🧪 Running {test_class_name}.{test_method_name}...")
    else:
        # Run all tests in the class
        suite = loader.loadTestsFromTestCase(test_classes[test_class_name])
        print(f"🧪 Running all tests in {test_class_name}...")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def quick_smoke_test():
    """Quick smoke test to verify basic functionality"""
    print("🚀 Running quick smoke test...\n")
    
    try:
        # Test basic CRUD for each model type
        print("Testing Recruiters...")
        recruiter = Recruiters(username="smoke_recruiter", email="smoke@test.com", password="pass")
        recruiter_id = recruiter.insert()
        assert recruiter_id is not None, "Failed to insert recruiter"
        
        retrieved = Recruiters.get(id=recruiter_id)
        assert retrieved is not None, "Failed to retrieve recruiter"
        assert retrieved.username == "smoke_recruiter", "Retrieved data mismatch"
        print("✓ Recruiters working")
        
        print("Testing Companies...")
        company = Companies(
            username="smoke_company", companyName="Smoke Corp", companyPhone="123",
            companyAddress="Smoke St", companyDescription="Test company", employeeSize=50
        )
        company_id = company.insert()
        assert company_id is not None, "Failed to insert company"
        print("✓ Companies working")
        
        print("Testing Skills...")
        skill = Skills(skill="Smoke Testing")
        skill_id = skill.insert()
        assert skill_id is not None, "Failed to insert skill"
        print("✓ Skills working")
        
        print("Testing JobPosts...")
        job_post = JobPosts(
            recruiterId=recruiter_id,
            companyId=company_id,
            title="Smoke Test Job",
            description="Testing job",
            experience=1,
            jobType="FULL_TIME",
            location="Remote",
            salary=50000.0,
            validTill="2025-12-31"
        )
        job_id = job_post.insert()
        assert job_id is not None, "Failed to insert job post"
        print("✓ JobPosts working")
        
        print("Testing PostSkills...")
        post_skill = PostSkills(
            postId=job_id,
            skillId=skill_id,
            isRequired=True
        )
        result = post_skill.insert()
        assert result is not None, "Failed to insert post skill"
        print("✓ PostSkills working")
        
        print("\n✅ Smoke test passed! All basic operations working.")
        return True
        
    except Exception as e:
        print(f"\n❌ Smoke test failed: {e}")
        return False


def test_data_consistency():
    """Test data consistency across related tables"""
    print("🔍 Testing data consistency...\n")
    
    try:
        # Create full workflow
        recruiter = Recruiters(username="consistency_recruiter", email="cr@test.com", password="pass")
        recruiter_id = recruiter.insert()
        
        freelancer = Freelancers(username="consistency_freelancer", email="cf@test.com", password="pass")
        freelancer_id = freelancer.insert()
        
        company = Companies(
            username="consistency_company", companyName="Consistency Corp", companyPhone="123",
            companyAddress="Consistency St", companyDescription="Test company", employeeSize=25
        )
        company_id = company.insert()
        
        # Test recruiter-company relationship
        recruiter_company = RecruiterCompanies(
            recruiterId=recruiter_id,
            companyId=company_id,
            role="ADMIN"
        )
        recruiter_company.insert()
        
        # Create job post
        job_post = JobPosts(
            recruiterId=recruiter_id,
            companyId=company_id,
            title="Consistency Test Job",
            description="Testing consistency",
            experience=2,
            jobType="FULL_TIME",
            location="Remote",
            salary=60000.0,
            validTill="2025-12-31"
        )
        job_id = job_post.insert()
        
        # Create skills and assign to job
        python_skill = Skills(skill="Python")
        python_id = python_skill.insert()
        
        react_skill = Skills(skill="React")
        react_id = react_skill.insert()
        
        # Assign skills to job post
        PostSkills(postId=job_id, skillId=python_id, isRequired=True).insert()
        PostSkills(postId=job_id, skillId=react_id, isRequired=False).insert()
        
        # Assign skills to freelancer
        FreelancerSkills(
            freelancerId=freelancer_id, 
            skillId=python_id, 
            proficiencyLevel="ADVANCED", 
            yearsOfExperience=4
        ).insert()
        
        FreelancerSkills(
            freelancerId=freelancer_id, 
            skillId=react_id, 
            proficiencyLevel="INTERMEDIATE", 
            yearsOfExperience=2
        ).insert()
        
        # Create resume
        pdf_data = b"dummy pdf content for consistency test"
        resume = Resumes(
            freelancerId=freelancer_id,
            name="consistency_resume.pdf",
            pdfData=pdf_data,
            fileSize=len(pdf_data),
            isDefault=True
        )
        resume_id = resume.insert()
        
        # Create application
        application = Applications(
            jobPostId=job_id,
            freelancerId=freelancer_id,
            resumeId=resume_id,
            coverLetter="Consistency test application"
        )
        app_id = application.insert()
        
        # Verify all relationships exist
        assert Recruiters.get(id=recruiter_id) is not None
        assert Companies.get(id=company_id) is not None
        assert JobPosts.get(id=job_id) is not None
        assert Applications.get(id=app_id) is not None
        assert len(PostSkills.getAll(postId=job_id)) == 2
        assert len(FreelancerSkills.getAll(freelancerId=freelancer_id)) == 2
        
        print("✅ Data consistency test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Data consistency test failed: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "smoke":
            quick_smoke_test()
        elif command == "consistency":
            test_data_consistency()
        elif command == "all":
            run_all_tests()
        elif command.startswith("test"):
            # Run specific test class
            if len(sys.argv) > 2:
                run_specific_test(sys.argv[1], sys.argv[2])
            else:
                run_specific_test(sys.argv[1])
        else:
            print("Usage:")
            print("  python tests.py all           # Run all tests")
            print("  python tests.py smoke         # Quick smoke test")
            print("  python tests.py consistency   # Data consistency test")
            print("  python tests.py TestDataModels # Run specific test class")
            print("  python tests.py TestDataModels test_recruiters_crud # Run specific test method")
    else:
        # Default: run all tests
        print("No command specified, running all tests...\n")
        run_all_tests()


# Additional utility functions for testing
def create_sample_data():
    """Create sample data for manual testing"""
    print("📝 Creating sample data...\n")
    
    try:
        # Create recruiters
        recruiter1 = Recruiters(username="john_recruiter", email="john.r@techcorp.com", password="password123")
        recruiter1_id = recruiter1.insert()
        
        recruiter2 = Recruiters(username="sarah_recruiter", email="sarah.r@innovate.com", password="password123")
        recruiter2_id = recruiter2.insert()
        
        # Create companies
        company1 = Companies(
            username="techcorp",
            companyName="TechCorp Industries",
            companyPhone="+1-555-0123",
            companyAddress="123 Silicon Valley Blvd, CA",
            companyDescription="Leading technology solutions provider",
            employeeSize=500
        )
        company1_id = company1.insert()
        
        company2 = Companies(
            username="innovate_startup",
            companyName="Innovate Startup",
            companyPhone="+1-555-0456",
            companyAddress="456 Innovation Ave, NY",
            companyDescription="Cutting-edge AI startup",
            employeeSize=25
        )
        company2_id = company2.insert()
        
        # Create skills
        skills_data = ["Python", "JavaScript", "React", "Node.js", "SQL", "Machine Learning", "Docker", "AWS"]
        skill_ids = {}
        for skill_name in skills_data:
            skill = Skills(skill=skill_name)
            skill_ids[skill_name] = skill.insert()
        
        # Create freelancers
        freelancer1 = Freelancers(username="alice_dev", email="alice@dev.com", password="password123")
        freelancer1_id = freelancer1.insert()
        
        freelancer2 = Freelancers(username="bob_fullstack", email="bob@fullstack.com", password="password123")
        freelancer2_id = freelancer2.insert()
        
        # Assign skills to freelancers
        FreelancerSkills(
            freelancerId=freelancer1_id, skillId=skill_ids["Python"], 
            proficiencyLevel="EXPERT", yearsOfExperience=5
        ).insert()
        
        FreelancerSkills(
            freelancerId=freelancer1_id, skillId=skill_ids["Machine Learning"], 
            proficiencyLevel="ADVANCED", yearsOfExperience=3
        ).insert()
        
        FreelancerSkills(
            freelancerId=freelancer2_id, skillId=skill_ids["JavaScript"], 
            proficiencyLevel="EXPERT", yearsOfExperience=4
        ).insert()
        
        FreelancerSkills(
            freelancerId=freelancer2_id, skillId=skill_ids["React"], 
            proficiencyLevel="ADVANCED", yearsOfExperience=3
        ).insert()
        
        # Create job posts
        job1 = JobPosts(
            recruiterId=recruiter1_id,
            companyId=company1_id,
            title="Senior Python Developer",
            description="We are looking for an experienced Python developer to join our AI team.",
            experience=3,
            jobType="FULL_TIME",
            location="San Francisco, CA",
            salary=120000.0,
            validTill="2025-10-31"
        )
        job1_id = job1.insert()
        
        job2 = JobPosts(
            recruiterId=recruiter2_id,
            companyId=company2_id,
            title="Full Stack Developer",
            description="Join our startup as a full stack developer working with modern web technologies.",
            experience=2,
            jobType="FULL_TIME",
            location="New York, NY",
            salary=95000.0,
            validTill="2025-11-30"
        )
        job2_id = job2.insert()
        
        # Assign skills to job posts
        PostSkills(postId=job1_id, skillId=skill_ids["Python"], isRequired=True).insert()
        PostSkills(postId=job1_id, skillId=skill_ids["Machine Learning"], isRequired=True).insert()
        PostSkills(postId=job1_id, skillId=skill_ids["SQL"], isRequired=False).insert()
        
        PostSkills(postId=job2_id, skillId=skill_ids["JavaScript"], isRequired=True).insert()
        PostSkills(postId=job2_id, skillId=skill_ids["React"], isRequired=True).insert()
        PostSkills(postId=job2_id, skillId=skill_ids["Node.js"], isRequired=False).insert()
        
        # Create experiences for freelancers
        Experiences(
            freelancerId=freelancer1_id,
            companyName="Previous AI Corp",
            startDate="2022-01-01",
            endDate="2024-06-30",
            role="ML Engineer",
            description="Developed machine learning models for recommendation systems"
        ).insert()
        
        Experiences(
            freelancerId=freelancer2_id,
            companyName="Web Solutions Inc",
            startDate="2021-03-01",
            endDate=None,  # Current position
            role="Full Stack Developer",
            description="Building modern web applications with React and Node.js"
        ).insert()
        
        # Create educations
        Educations(
            freelancerId=freelancer1_id,
            course="Computer Science",
            degree="Master's",
            school="Stanford University",
            startDate="2018-09-01",
            endDate="2020-06-01",
            cgpa=9.2
        ).insert()
        
        Educations(
            freelancerId=freelancer2_id,
            course="Software Engineering",
            degree="Bachelor's",
            school="MIT",
            startDate="2017-09-01",
            endDate="2021-05-01",
            cgpa=8.8
        ).insert()
        
        # Create resumes
        pdf_data1 = b"Alice's resume PDF content would be here..."
        resume1 = Resumes(
            freelancerId=freelancer1_id,
            name="Alice_Smith_Resume.pdf",
            pdfData=pdf_data1,
            fileSize=len(pdf_data1),
            isDefault=True
        )
        resume1_id = resume1.insert()
        
        pdf_data2 = b"Bob's resume PDF content would be here..."
        resume2 = Resumes(
            freelancerId=freelancer2_id,
            name="Bob_Johnson_Resume.pdf",
            pdfData=pdf_data2,
            fileSize=len(pdf_data2),
            isDefault=True
        )
        resume2_id = resume2.insert()
        
        # Create applications
        Applications(
            jobPostId=job1_id,
            freelancerId=freelancer1_id,
            resumeId=resume1_id,
            coverLetter="I am excited to apply for the Senior Python Developer position. My experience in machine learning aligns perfectly with your requirements.",
            status="PENDING"
        ).insert()
        
        Applications(
            jobPostId=job2_id,
            freelancerId=freelancer2_id,
            resumeId=resume2_id,
            coverLetter="I would love to join your startup as a Full Stack Developer. My skills in React and Node.js make me a great fit.",
            status="UNDER_REVIEW"
        ).insert()
        
        # Create recruiter-company relationships
        RecruiterCompanies(
            recruiterId=recruiter1_id,
            companyId=company1_id,
            role="ADMIN"
        ).insert()
        
        RecruiterCompanies(
            recruiterId=recruiter2_id,
            companyId=company2_id,
            role="RECRUITER"
        ).insert()
        
        print("✅ Sample data created successfully!")
        print("\nSample data includes:")
        print("- 2 Recruiters")
        print("- 2 Companies") 
        print("- 2 Freelancers")
        print("- 8 Skills")
        print("- 2 Job Posts")
        print("- 2 Applications")
        print("- Skills assignments and relationships")
        print("- Experience and education records")
        print("- Resume uploads")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False


def validate_schema_consistency():
    """Validate that models match database schema"""
    print("🔍 Validating schema consistency...\n")
    
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        
        # Check all tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = {row[0] for row in cursor.fetchall()}
        
        expected_tables = {
            "Recruiters", "Freelancers", "Companies", "Skills", "JobPosts",
            "Experiences", "Educations", "Resumes", "PostSkills", 
            "RecruiterCompanies", "FreelancerSkills", "Applications"
        }
        
        missing_tables = expected_tables - existing_tables
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False
        
        print("✅ All expected tables exist")
        
        # Validate table structures match models
        validation_queries = {
            "Recruiters": "SELECT id, username, email, password, createdAt, updatedAt FROM Recruiters LIMIT 0",
            "Skills": "SELECT id, skill, createdAt, updatedAt FROM Skills LIMIT 0",
            "Applications": "SELECT id, jobPostId, freelancerId, status, appliedOn, resumeId, coverLetter, createdAt, updatedAt FROM Applications LIMIT 0"
        }
        
        for table, query in validation_queries.items():
            try:
                cursor.execute(query)
                print(f"✅ {table} schema matches model")
            except sqlite3.Error as e:
                print(f"❌ {table} schema mismatch: {e}")
                return False
        
        conn.close()
        print("\n✅ Schema consistency validation passed!")
        return True
        
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False


# Test runner functions
def run_tests_with_sample_data():
    """Run tests with sample data for more realistic testing"""
    print("🧪 Running tests with sample data...\n")
    
    # Create sample data first
    if not create_sample_data():
        print("❌ Failed to create sample data, aborting tests")
        return False
    
    # Run subset of tests that work with existing data
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests that don't clear data
    suite.addTest(TestDatabaseFunctions('test_fetch_function'))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


print("""
🧪 Model Testing Suite
=====================

Available commands:
  python tests.py                    # Run all tests
  python tests.py smoke              # Quick smoke test
  python tests.py consistency        # Data consistency test
  python tests.py all                # Full test suite
  python tests.py TestDataModels     # Run specific test class
  
Additional functions:
  create_sample_data()               # Create sample data for manual testing
  validate_schema_consistency()      # Check model-schema alignment
  run_tests_with_sample_data()       # Test with realistic data

Example usage in Python:
  >>> from tests import *
  >>> quick_smoke_test()
  >>> create_sample_data()
  >>> validate_schema_consistency()
""")