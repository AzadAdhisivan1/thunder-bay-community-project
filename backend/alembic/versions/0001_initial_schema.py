"""Initial schema: categories and services (US-01)

Revision ID: 0001
Revises:
Create Date: 2026-10-26
"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PostGIS is used for distance queries from Sprint 2 (US-06).
    if op.get_bind().dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("slug", sa.String(100), nullable=False),
    )
    op.create_index("ix_categories_slug", "categories", ["slug"], unique=True)

    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("address", sa.String(300), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("hours", sa.Text()),
        sa.Column("phone", sa.String(50)),
        sa.Column("website", sa.String(300)),
        sa.Column("eligibility", sa.Text()),
        sa.Column(
            "last_updated",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("name", "address", name="uq_service_name_address"),
    )
    op.create_index("ix_services_name", "services", ["name"])
    op.create_index("ix_services_category_id", "services", ["category_id"])


def downgrade() -> None:
    op.drop_table("services")
    op.drop_table("categories")
