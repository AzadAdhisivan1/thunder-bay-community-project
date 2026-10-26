from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import ServiceOut

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=list[ServiceOut])
def list_services(category: str | None = None, db: Session = Depends(get_db)):
    """US-02: list services, filtered by category slug when `category` is given.

    Owner: Santhosh.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet (US-02)")


@router.get("/{service_id}", response_model=ServiceOut)
def get_service(service_id: int, db: Session = Depends(get_db)):
    """US-04: one service by id. Return 404 "Service not found" if it doesn't exist.

    Owner: Santhosh (API) for Kamakshi's details page.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet (US-04)")
