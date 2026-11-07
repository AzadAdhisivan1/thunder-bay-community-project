"""Optional location parameters shared by the service endpoints (US-06)."""

from dataclasses import dataclass

from fastapi import HTTPException, Query

from app.geo import GeoPoint

MAX_RADIUS_KM = 100.0  # Thunder Bay and the surrounding area; also caps work per request.


@dataclass(frozen=True)
class LocationFilter:
    near: GeoPoint | None
    max_km: float | None


def location_params(
    lat: float | None = Query(None, ge=-90, le=90, description="Your latitude (WGS 84)"),
    lng: float | None = Query(None, ge=-180, le=180, description="Your longitude (WGS 84)"),
    max_km: float | None = Query(
        None, gt=0, le=MAX_RADIUS_KM, description="Only services within this many km; needs lat and lng"
    ),
) -> LocationFilter:
    if (lat is None) != (lng is None):
        raise HTTPException(status_code=422, detail="lat and lng must be given together")
    if max_km is not None and lat is None:
        raise HTTPException(status_code=422, detail="max_km needs lat and lng")
    near = GeoPoint(lat, lng) if lat is not None else None
    return LocationFilter(near=near, max_km=max_km)
