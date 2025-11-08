#!/usr/bin/env python3
"""Create the jobs table from models.py"""

import os
from dotenv import load_dotenv
load_dotenv()

from models import Base, Job
from sqlalchemy import create_engine

# Get database URL
db_url = os.getenv('DATABASE_URL')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

# Create engine
engine = create_engine(db_url)

# Create jobs table
Base.metadata.create_all(engine)

print("[SUCCESS] Jobs table created/verified")
