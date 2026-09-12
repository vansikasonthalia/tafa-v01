"""
Tracking router — list and delete tracking entries (signal history).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import TrackingEntry

router = APIRouter(prefix="/api/tracking", tags=["tracking"])


@router.get("")
def list_tracking_entries(
    signal: str | None = Query(None, description="Filter by signal: BUY or SELL"),
    limit: int = Query(100, description="Max entries to return"),
    db: Session = Depends(get_db),
):
    """List all tracking entries, optionally filtered by signal type."""
    query = db.query(TrackingEntry).order_by(TrackingEntry.timestamp.desc())

    if signal and signal.upper() in ("BUY", "SELL"):
        query = query.filter(TrackingEntry.signal == signal.upper())

    entries = query.limit(limit).all()

    return {
        "total": len(entries),
        "entries": [e.to_dict() for e in entries],
    }


@router.delete("/{entry_id}")
def delete_tracking_entry(entry_id: int, db: Session = Depends(get_db)):
    """Delete a single tracking entry by ID."""
    entry = db.query(TrackingEntry).filter(TrackingEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail=f"Tracking entry {entry_id} not found.")
    db.delete(entry)
    db.commit()
    return {"deleted": entry_id}
