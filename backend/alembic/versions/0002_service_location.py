"""PostGIS location column for distance queries (US-06)

Adds services.location, a geography point that PostgreSQL computes from latitude and
longitude, plus a GiST index so radius queries stay fast. Because the database
generates it, the seed script and the CSV don't change and the column can never
disagree with the coordinates.

SQLite (used by the unit tests) has no PostGIS, so there this migration does nothing
and the app computes distances in Python instead (see app/crud/distance.py).

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-07
"""
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    op.execute(
        """
        ALTER TABLE services
        ADD COLUMN location geography(Point, 4326)
        GENERATED ALWAYS AS (
            ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography
        ) STORED
        """
    )
    op.execute("CREATE INDEX ix_services_location ON services USING GIST (location)")


def downgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    op.execute("DROP INDEX IF EXISTS ix_services_location")
    op.execute("ALTER TABLE services DROP COLUMN IF EXISTS location")
