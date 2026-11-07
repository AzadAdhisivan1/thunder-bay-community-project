from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud import search
from app.crud.distance import with_distance
from app.db import get_db
from app.routers.location import LocationFilter, location_params
from app.schemas import ServiceOut

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=list[ServiceOut])
def search_services(
    q: str = Query(min_length=1),
    location: LocationFilter = Depends(location_params),
    db: Session = Depends(get_db),
):
    query = q.strip()
    if not query:
        raise HTTPException(status_code=422, detail="Search query must not be blank")
    if location.near is None:
        return search.search_services(db, query)
    rows = with_distance(db, search.search_query(query), location.near, location.max_km)
    return [ServiceOut.with_distance(service, km) for service, km in rows]
