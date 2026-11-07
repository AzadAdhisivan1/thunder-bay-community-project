from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import services
from app.crud.distance import with_distance
from app.db import get_db
from app.routers.location import LocationFilter, location_params
from app.schemas import ServiceOut

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=list[ServiceOut])
def list_services(
    category: str | None = None,
    location: LocationFilter = Depends(location_params),
    db: Session = Depends(get_db),
):
    if location.near is None:
        return services.list_services(db, category)
    rows = with_distance(db, services.services_query(category), location.near, location.max_km)
    return [ServiceOut.with_distance(service, km) for service, km in rows]


@router.get("/{service_id}", response_model=ServiceOut)
def get_service(
    service_id: int,
    location: LocationFilter = Depends(location_params),
    db: Session = Depends(get_db),
):
    if location.near is None:
        service = services.get_service(db, service_id)
        if service is None:
            raise HTTPException(status_code=404, detail="Service not found")
        return service
    # A radius doesn't hide a single service: the details page always shows it.
    rows = with_distance(db, services.service_query(service_id), location.near)
    if not rows:
        raise HTTPException(status_code=404, detail="Service not found")
    return ServiceOut.with_distance(*rows[0])
