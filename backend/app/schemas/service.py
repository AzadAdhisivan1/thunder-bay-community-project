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
