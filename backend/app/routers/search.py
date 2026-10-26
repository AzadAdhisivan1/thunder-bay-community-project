from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import ServiceOut

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=list[ServiceOut])
def search_services(q: str = Query(min_length=1), db: Session = Depends(get_db)):
    """US-03: keyword search over service name, category and description.

    Owner: Santhosh. Empty queries are rejected with 422 by `min_length=1`.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet (US-03)")
