from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.setup import get_db
from database.models import User
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "zeroday-api"
    }

@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    checks = {
        "api": "healthy",
        "database": "unknown",
        "demo_data": "unknown"
    }
    
    try:
        user_count = db.query(User).count()
        checks["database"] = "healthy"
        checks["user_count"] = user_count
    except Exception:
        checks["database"] = "unhealthy"
    
    try:
        demo_scenarios = ["startup", "enterprise", "freelancer"]
        missing_scenarios = []
        for scenario in demo_scenarios:
            if not os.path.exists(f"demo/scenarios/{scenario}_scenario.json"):
                missing_scenarios.append(scenario)
        
        if missing_scenarios:
            checks["demo_data"] = "degraded"
            checks["missing_scenarios"] = missing_scenarios
        else:
            checks["demo_data"] = "healthy"
            checks["available_scenarios"] = demo_scenarios
    except Exception:
        checks["demo_data"] = "unhealthy"
    
    overall_status = "healthy"
    if any(status == "unhealthy" for status in checks.values() if isinstance(status, str)):
        overall_status = "unhealthy"
    elif any(status == "degraded" for status in checks.values() if isinstance(status, str)):
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "zeroday-api",
        "checks": checks
    }

@router.get("/version")
async def get_version():
    return {
        "version": "1.0.0",
        "build": "phase-2",
        "environment": os.getenv("ENVIRONMENT", "development")
    }