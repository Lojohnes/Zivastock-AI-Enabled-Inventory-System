"""Add forecast results and inventory exposure predictions.

Revision ID: 009
Revises: 008
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    json_type = lambda: postgresql.JSONB(astext_type=sa.Text())
    op.create_table(
        "forecast_results",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("location_id", sa.BigInteger(), nullable=True),
        sa.Column("model_version_id", sa.BigInteger(), nullable=True),
        sa.Column("model_algorithm", sa.String(length=50), nullable=False),
        sa.Column("forecast_date", sa.Date(), nullable=False),
        sa.Column("horizon_days", sa.Integer(), nullable=False, server_default="7"),
        sa.Column("predicted_demand", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("lower_bound", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("upper_bound", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("actual_demand", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("evaluation_metrics", json_type(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["model_version_id"], ["model_versions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("product_id", "location_id", "model_version_id", "forecast_date"):
        op.create_index(f"ix_forecast_results_{column}", "forecast_results", [column])

    op.create_table(
        "inventory_exposures",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("location_id", sa.BigInteger(), nullable=True),
        sa.Column("calculation_date", sa.Date(), nullable=False),
        sa.Column("forecast_model", sa.String(length=50), nullable=False),
        sa.Column("current_quantity", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("predicted_daily_demand", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("safety_stock", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("days_until_stockout", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("stockout_date", sa.Date(), nullable=True),
        sa.Column("stockout_risk", sa.String(length=20), nullable=False, server_default="LOW"),
        sa.Column("excess_quantity", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("slow_moving", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("non_moving", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("explanation", json_type(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("calculation_version", sa.String(length=50), nullable=False, server_default="v1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("stockout_risk IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name="chk_exposure_stockout_risk"),
        sa.CheckConstraint("slow_moving IN (0, 1)", name="chk_exposure_slow_moving"),
        sa.CheckConstraint("non_moving IN (0, 1)", name="chk_exposure_non_moving"),
    )
    for column in ("product_id", "location_id", "calculation_date"):
        op.create_index(f"ix_inventory_exposures_{column}", "inventory_exposures", [column])


def downgrade() -> None:
    for column in ("calculation_date", "location_id", "product_id"):
        op.drop_index(f"ix_inventory_exposures_{column}", table_name="inventory_exposures")
    op.drop_table("inventory_exposures")
    for column in ("forecast_date", "model_version_id", "location_id", "product_id"):
        op.drop_index(f"ix_forecast_results_{column}", table_name="forecast_results")
    op.drop_table("forecast_results")
