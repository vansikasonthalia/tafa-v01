"""
Health check router.
"""

from fastapi import APIRouter
from ..services.scheduler import get_scheduler_status

router = APIRouter(tags=["default"])


@router.get("/api/health")
def health():
    """Health check endpoint."""
    scheduler = get_scheduler_status()
    return {
        "status": "ok",
        "app": "TAFA V1",
        "scheduler": scheduler,
    }
