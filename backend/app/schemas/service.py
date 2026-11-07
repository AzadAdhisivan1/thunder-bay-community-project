from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.category import CategoryOut


class ServiceOut(BaseModel):
    """The service shape every endpoint returns. See docs/api.md."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: CategoryOut
    description: str | None
    address: str
    latitude: float
    longitude: float
    hours: str | None
    phone: str | None
    website: str | None
    eligibility: str | None
    last_updated: datetime
    # Kilometres from the location in the request (US-06); null when none was given.
    distance_km: float | None = None

    @classmethod
    def with_distance(cls, service, distance_km: float) -> "ServiceOut":
        return cls.model_validate(service).model_copy(
            update={"distance_km": round(distance_km, 2)}
        )
