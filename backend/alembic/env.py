from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app import models  # noqa: F401  (registers all tables on Base.metadata)
from app.config import settings
from app.db import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Database objects that exist only in PostgreSQL and are managed by hand-written
# migrations, not by the models. Without this, autogenerate would try to drop them.
POSTGIS_ONLY = {"location", "ix_services_location"}


def include_object(obj, name, type_, reflected, compare_to):
    """Tell autogenerate which database objects belong to the app."""
    if reflected and compare_to is None:
        # Tables in the database but not in our models: the PostGIS image's own
        # tables (spatial_ref_sys, the tiger geocoder, topology). Never drop them.
        if type_ == "table":
            return False
        if name in POSTGIS_ONLY:
            return False
    return True


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, include_object=include_object
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
