# Import every model here so Alembic and the tests see all tables.
from app.models.category import Category
from app.models.service import Service

__all__ = ["Category", "Service"]
