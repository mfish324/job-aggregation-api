"""
Reset Railway Database - Delete all jobs and recreate tables

This script will:
1. Connect to Railway PostgreSQL database
2. Drop all job-related tables
3. Recreate tables with proper schema
4. Ready for fresh scraping
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from models import Base as AggregatorBase
from job_board_integration import Base as JobBoardBase

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

load_dotenv()

def reset_database():
    """Reset the database - drop and recreate all tables"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        print("   For Railway: Get URL from Railway dashboard → Variables")
        return False
    
    print("=" * 60)
    print("DATABASE RESET")
    print("=" * 60)
    print(f"Database: {database_url.split('@')[1] if '@' in database_url else 'local'}")
    print()
    
    # Confirm
    confirm = input("⚠️  This will DELETE ALL JOBS. Type 'YES' to confirm: ")
    if confirm != 'YES':
        print("❌ Cancelled")
        return False
    
    try:
        engine = create_engine(database_url)
        
        print("\n1. Dropping existing tables...")
        with engine.connect() as conn:
            # Drop tables
            conn.execute(text("DROP TABLE IF EXISTS job_listings CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS jobs CASCADE"))
            conn.commit()
            print("   ✅ Tables dropped")
        
        print("\n2. Creating aggregator tables (jobs)...")
        AggregatorBase.metadata.create_all(engine)
        print("   ✅ Aggregator tables created")
        
        print("\n3. Creating job board tables (job_listings)...")
        JobBoardBase.metadata.create_all(engine)
        print("   ✅ Job board tables created")
        
        print("\n4. Verifying tables...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            print(f"   Tables created: {', '.join(tables)}")
            
            if 'jobs' in tables and 'job_listings' in tables:
                print("   ✅ All tables verified")
            else:
                print("   ⚠️  Some tables missing!")
        
        print("\n" + "=" * 60)
        print("✅ DATABASE RESET COMPLETE")
        print("=" * 60)
        print("\nDatabase is now empty and ready for scraping.")
        print("\nNext steps:")
        print("1. Run: python trigger_scrape.py --url [railway-url] --sources google amazon")
        print("2. Or use Railway API: POST /scrape")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = reset_database()
    exit(0 if success else 1)
