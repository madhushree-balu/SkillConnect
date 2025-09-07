import sqlite3
from db.sql_commands import createTable, createIndexes


def create_database():
    """
    Creates all tables, indexes, and triggers for the job marketplace database.
    Returns True if successful, False otherwise.
    """
    conn = None
    try:
        conn = sqlite3.connect("database.db")
        
        # Enable foreign keys and configure database
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("PRAGMA journal_mode = WAL")
        cursor.execute("PRAGMA busy_timeout = 30000")
        
        print("Creating database tables...")
        
        # Define table creation order to respect foreign key dependencies
        table_order = [
            "Recruiters",
            "Freelancers", 
            "Companies",
            "Skills",
            "JobPosts",
            "Experiences",
            "Educations",
            "Resumes",
            "PostSkills",
            "RecruiterCompanies", 
            "FreelancerSkills",
            "Applications",
            "FreelancerDetails"
        ]
        
        # Create tables in proper order
        for table_name in table_order:
            if table_name in createTable:
                cursor.execute(createTable[table_name])
                print(f"✓ Created table: {table_name}")
            else:
                print(f"⚠ Warning: Table '{table_name}' not found in createTable dict")
        
        print("\nCreating indexes for better performance...")
        
        # Create indexes
        for index_name, index_query in createIndexes.items():
            cursor.execute(index_query)
            print(f"✓ Created index: {index_name}")
        
        print("\nCreating triggers for automatic timestamp updates...")
        
        # Create triggers for updatedAt timestamp updates
        trigger_queries = [
            """
            CREATE TRIGGER IF NOT EXISTS update_recruiters_timestamp 
            AFTER UPDATE ON Recruiters
            BEGIN
                UPDATE Recruiters SET updatedAt = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """,
            """
            CREATE TRIGGER IF NOT EXISTS update_freelancers_timestamp 
            AFTER UPDATE ON Freelancers
            BEGIN
                UPDATE Freelancers SET updatedAt = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """,
            """
            CREATE TRIGGER IF NOT EXISTS update_companies_timestamp 
            AFTER UPDATE ON Companies
            BEGIN
                UPDATE Companies SET updatedAt = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """,
            """
            CREATE TRIGGER IF NOT EXISTS update_skills_timestamp 
            AFTER UPDATE ON Skills
            BEGIN
                UPDATE Skills SET updatedAt = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """,
            """
            CREATE TRIGGER IF NOT EXISTS update_jobposts_timestamp 
            AFTER UPDATE ON JobPosts
            BEGIN
                UPDATE JobPosts SET updatedAt = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """,
            """
            CREATE TRIGGER IF NOT EXISTS update_experiences_timestamp 
            AFTER UPDATE ON Experiences
            BEGIN
                UPDATE Experiences SET updatedAt = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """,
            """
            CREATE TRIGGER IF NOT EXISTS update_educations_timestamp 
            AFTER UPDATE ON Educations
            BEGIN
                UPDATE Educations SET updatedAt = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """,
            """
            CREATE TRIGGER IF NOT EXISTS update_resumes_timestamp 
            AFTER UPDATE ON Resumes
            BEGIN
                UPDATE Resumes SET updatedAt = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """,
            """
            CREATE TRIGGER IF NOT EXISTS update_applications_timestamp 
            AFTER UPDATE ON Applications
            BEGIN
                UPDATE Applications SET updatedAt = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """
        ]
        
        for trigger_query in trigger_queries:
            cursor.execute(trigger_query)
            
        print("✓ Created automatic timestamp update triggers")
        
        # Commit all changes
        conn.commit()
        conn.close()
        
        print("\n🎉 Database setup completed successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Database error during setup: {e}")
        if conn:
            conn.close()
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        if conn:
            conn.close()
        return False


def drop_all_tables():
    """
    Drops all tables in reverse order to avoid foreign key conflicts.
    Use with caution - this will delete all data!
    """
    conn = None
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        
        # Disable foreign key constraints temporarily
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        print("Dropping all tables...")
        
        # Drop tables in reverse order (updated to PascalCase)
        table_order = [
            "Applications",
            "FreelancerSkills", 
            "RecruiterCompanies",
            "PostSkills",
            "Resumes",
            "Educations",
            "Experiences",
            "JobPosts",
            "Skills",
            "Companies",
            "Freelancers",
            "Recruiters"
        ]
        
        for table_name in table_order:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            print(f"✓ Dropped table: {table_name}")
        
        # Re-enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        conn.commit()
        conn.close()
        
        print("\n✅ All tables dropped successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Database error during table drop: {e}")
        if conn:
            conn.close()
        return False


def reset_database():
    """
    Completely resets the database by dropping all tables and recreating them.
    """
    print("🔄 Resetting database...\n")
    
    if drop_all_tables():
        print("\n" + "="*50)
        return create_database()
    else:
        print("❌ Failed to drop tables, aborting reset.")
        return False


def check_database_status():
    """
    Checks if all required tables exist in the database.
    """
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        
        # Get list of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = {row[0] for row in cursor.fetchall()}
        
        required_tables = set(createTable.keys())
        
        print("Database Status Check:")
        print("-" * 30)
        
        missing_tables = []
        for table in required_tables:
            if table in existing_tables:
                print(f"✓ {table}")
            else:
                print(f"❌ {table} (MISSING)")
                missing_tables.append(table)
        
        conn.close()
        
        if missing_tables:
            print(f"\n⚠ Missing tables: {', '.join(missing_tables)}")
            print("Run create_database() to create missing tables.")
            return False
        else:
            print("\n✅ All tables exist!")
            return True
            
    except sqlite3.Error as e:
        print(f"❌ Database error during status check: {e}")
        return False


# Convenience function to run setup
if __name__ == "__main__":
    # Example usage:
    create_database()          # Create all tables, indexes, and triggers
    check_database_status()    # Check what tables exist
    # reset_database()           # Drop and recreate everything
    pass