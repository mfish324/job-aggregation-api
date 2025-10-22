from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import hashlib

Base = declarative_base()


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    job_id = Column(String(255), unique=True, index=True)  # Hash for deduplication
    title = Column(String(500), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    location = Column(String(255), index=True)
    description = Column(Text)
    url = Column(String(1000), nullable=False)
    source = Column(String(100), nullable=False, index=True)
    posted_date = Column(DateTime, index=True)
    job_type = Column(String(100))
    salary = Column(String(255))
    tags = Column(Text)  # JSON string of tags/skills
    remote = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_job_id(title, company, location):
        """Generate unique job ID based on title, company, and location"""
        key = f"{title.lower().strip()}|{company.lower().strip()}|{location.lower().strip()}"
        return hashlib.md5(key.encode()).hexdigest()

    def __repr__(self):
        return f"<Job(title='{self.title}', company='{self.company}', source='{self.source}')>"


class DatabaseManager:
    def __init__(self, database_url='sqlite:///jobs.db'):
        # Add connection pooling and health checks for PostgreSQL
        engine_kwargs = {}
        if database_url.startswith('postgresql'):
            engine_kwargs.update({
                'pool_pre_ping': True,  # Verify connections before using
                'pool_recycle': 3600,   # Recycle connections after 1 hour
                'pool_size': 5,         # Max 5 connections in pool
                'max_overflow': 10,     # Allow up to 10 overflow connections
                'connect_args': {
                    'connect_timeout': 10
                }
            })

        self.engine = create_engine(database_url, **engine_kwargs)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_job(self, job_data):
        """Add a job to the database if it doesn't exist"""
        job_id = Job.generate_job_id(
            job_data['title'],
            job_data['company'],
            job_data.get('location', 'N/A')
        )

        existing = self.session.query(Job).filter_by(job_id=job_id).first()
        if existing:
            return False, existing

        job = Job(job_id=job_id, **job_data)
        self.session.add(job)
        self.session.commit()
        return True, job

    def get_jobs(self, filters=None, limit=100):
        """Retrieve jobs with optional filters"""
        query = self.session.query(Job)

        if filters:
            if 'source' in filters:
                query = query.filter_by(source=filters['source'])
            if 'remote' in filters:
                query = query.filter_by(remote=filters['remote'])
            if 'keyword' in filters:
                keyword = f"%{filters['keyword']}%"
                query = query.filter(
                    (Job.title.like(keyword)) |
                    (Job.description.like(keyword)) |
                    (Job.tags.like(keyword))
                )

        return query.order_by(Job.posted_date.desc()).limit(limit).all()

    def get_stats(self):
        """Get statistics about scraped jobs"""
        total = self.session.query(Job).count()
        by_source = {}
        for source, count in self.session.query(Job.source, func.count(Job.id)).group_by(Job.source).all():
            by_source[source] = count

        return {
            'total_jobs': total,
            'by_source': by_source
        }

    def close(self):
        self.session.close()
