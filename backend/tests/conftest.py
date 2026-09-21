import os

import pytest
from sqlalchemy import BigInteger, create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session


@compiles(BigInteger, "sqlite")
def compile_big_integer_for_sqlite(_type, compiler, **kwargs):
    return "INTEGER"

# The shell environment used by some development tools may expose DEBUG with a
# non-boolean value. Tests should always use the application development mode.
if os.environ.get("DEBUG", "").lower() not in {"true", "false", "1", "0", "yes", "no", "on", "off"}:
    os.environ["DEBUG"] = "True"

from app.core.database import Base
import app.models  # noqa: F401 - register all ORM models with Base.metadata


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    connection = engine.connect()
    transaction = connection.begin()

    table_names = {
        "roles",
        "users",
        "imports",
        "product_categories",
        "products",
        "locations",
        "shelves",
        "shelf_sections",
        "stocktake_sessions",
        "first_counts",
        "second_counts",
        "inventory_events",
        "data_quality_batches",
        "data_quality_issues",
        "inventory_feature_snapshots",
        "model_versions",
        "anomaly_results",
        "inventory_risk_scores",
        "forecast_results",
        "inventory_exposures",
        "ai_recommendations",
        "recommendation_decisions",
        "recommendation_outcomes",
    }
    tables = [table for table in Base.metadata.sorted_tables if table.name in table_names]
    Base.metadata.create_all(bind=connection, tables=tables)

    session = Session(bind=connection)
    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()
        engine.dispose()
