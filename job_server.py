"""
Job Server API - FastAPI REST API for Job Aggregation Platform

This server provides a REST API that your other job search platforms can call.

Features:
- RESTful endpoints for job search, scraping, and management
- Job board integration (lightweight database)
- Real-time job scraping
- Pagination, filtering, search
- CORS enabled for web apps
- OpenAPI/Swagger documentation
- Ready for Docker deployment

Usage:
    python job_server.py

Access:
    API: http://localhost:8000
    Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import uvicorn

from job_board_integration import JobBoardAPI
from aggregator import JobAggregator
import os

# Initialize FastAPI
app = FastAPI(
    title="Job Aggregation API",
    description="REST API for aggregating and serving job listings from multiple sources",
    version="1.0.0"
)

# Enable CORS for web apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize job board API
job_api = JobBoardAPI()

# Pydantic models for request/response
class JobResponse(BaseModel):
    id: int
    job_id: str
    title: str
    company: str
    location: str
    salary: Optional[str]
    source: str
    source_url: str
    posted_date: Optional[str]
    remote: bool
    job_type: Optional[str]
    preview_text: Optional[str]
    created_at: str

class JobDetailResponse(JobResponse):
    description: str
    view_count: int
    from_cache: bool

class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class ScrapeRequest(BaseModel):
    keywords: Optional[str] = None
    location: Optional[str] = None
    sources: Optional[List[str]] = None
    max_pages: int = 3

class ScrapeResponse(BaseModel):
    status: str
    total_scraped: int
    total_new: int
    total_duplicates: int
    by_source: dict

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """API root - basic info"""
    return {
        "name": "Job Aggregation API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "jobs": "/jobs",
            "job_detail": "/jobs/{id}",
            "scrape": "/scrape",
            "stats": "/stats"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        total_jobs = job_api.db.get_total_count()
        return {
            "status": "healthy",
            "database": "connected",
            "total_jobs": total_jobs
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/jobs", response_model=JobListResponse)
async def get_jobs(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Jobs per page"),
    keyword: Optional[str] = Query(None, description="Search keyword"),
    location: Optional[str] = Query(None, description="Job location"),
    source: Optional[str] = Query(None, description="Filter by source"),
    remote_only: bool = Query(False, description="Remote jobs only")
):
    """
    Get paginated list of jobs

    Examples:
    - /jobs?page=1&per_page=20
    - /jobs?keyword=python&remote_only=true
    - /jobs?source=remoteok&location=Remote
    """
    try:
        result = job_api.get_job_list(
            page=page,
            per_page=per_page,
            keyword=keyword,
            remote_only=remote_only,
            location=location
        )

        # Convert to response model
        return JobListResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}", response_model=JobDetailResponse)
async def get_job_detail(
    job_id: int,
    use_cache: bool = Query(True, description="Use cached description if available")
):
    """
    Get full job details including description

    This endpoint:
    - Fetches full job description on first call
    - Caches description for subsequent calls
    - Tracks view count
    """
    try:
        details = job_api.get_job_details(job_id, use_cache=use_cache)

        if not details:
            raise HTTPException(status_code=404, detail="Job not found")

        return JobDetailResponse(**details)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_jobs(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger job scraping from sources

    This will:
    1. Scrape jobs from specified sources (or all if none specified)
    2. Add new jobs to database
    3. Return statistics

    Note: Scraping runs in background. Use /scrape/status/{task_id} to check progress.
    """
    try:
        aggregator = JobAggregator()

        # Scrape jobs
        stats = aggregator.scrape_all(
            keywords=request.keywords,
            location=request.location,
            sources=request.sources,
            max_pages=request.max_pages
        )

        # Import new jobs to job board database
        background_tasks.add_task(import_to_job_board)

        aggregator.close()

        return ScrapeResponse(
            status="completed",
            total_scraped=stats['total_scraped'],
            total_new=stats['total_new'],
            total_duplicates=stats['total_duplicates'],
            by_source=stats['by_source']
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_statistics():
    """
    Get database statistics

    Returns:
    - Total jobs
    - Remote jobs count
    - Jobs by source
    - Recent activity
    """
    try:
        stats = job_api.get_statistics()

        # Add additional stats
        from sqlalchemy import func
        from job_board_integration import JobListing
        from datetime import timedelta

        # Jobs added in last 24 hours
        recent_cutoff = datetime.utcnow() - timedelta(days=1)
        recent_jobs = job_api.db.session.query(JobListing).filter(
            JobListing.created_at >= recent_cutoff
        ).count()

        # Jobs with salary info
        with_salary = job_api.db.session.query(JobListing).filter(
            JobListing.salary.isnot(None),
            JobListing.salary != ''
        ).count()

        stats['recent_jobs_24h'] = recent_jobs
        stats['jobs_with_salary'] = with_salary
        stats['salary_percentage'] = round(with_salary / stats['total_jobs'] * 100, 1) if stats['total_jobs'] > 0 else 0

        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sources")
async def get_sources():
    """
    Get list of available job sources
    """
    return {
        "sources": [
            {
                "id": "remoteok",
                "name": "RemoteOK",
                "type": "api",
                "requires_key": False,
                "active": True
            },
            {
                "id": "remotive",
                "name": "Remotive",
                "type": "api",
                "requires_key": False,
                "active": True
            },
            {
                "id": "weworkremotely",
                "name": "We Work Remotely",
                "type": "scraper",
                "requires_key": False,
                "active": True
            },
            {
                "id": "authenticjobs",
                "name": "Authentic Jobs",
                "type": "rss",
                "requires_key": False,
                "active": True
            },
            {
                "id": "github",
                "name": "GitHub",
                "type": "api",
                "requires_key": False,
                "active": True
            },
            {
                "id": "indeed",
                "name": "Indeed (RapidAPI)",
                "type": "api",
                "requires_key": True,
                "active": bool(os.getenv('RAPIDAPI_KEY'))
            }
        ]
    }

@app.post("/import")
async def import_from_aggregator():
    """
    Import jobs from aggregator database to job board database

    Use this after scraping to update the job board with new jobs.
    """
    try:
        imported, skipped = job_api.import_from_aggregator()
        return {
            "status": "success",
            "imported": imported,
            "skipped": skipped,
            "total": job_api.db.get_total_count()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Background task
async def import_to_job_board():
    """Background task to import scraped jobs"""
    try:
        job_api.import_from_aggregator()
    except Exception as e:
        print(f"Background import error: {e}")

# =============================================================================
# STARTUP/SHUTDOWN
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("="*80)
    print("JOB AGGREGATION API SERVER")
    print("="*80)
    print(f"Server starting...")
    print(f"Total jobs in database: {job_api.db.get_total_count()}")
    print(f"\nAPI Documentation: http://localhost:8000/docs")
    print(f"Interactive API: http://localhost:8000/redoc")
    print("="*80)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    job_api.close()
    print("Server shutdown complete")

# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    import os
    port = int(os.getenv("API_PORT", "8001"))  # Use port 8001 to avoid conflicts
    uvicorn.run(
        "job_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Auto-reload on code changes (disable in production)
        log_level="info"
    )
