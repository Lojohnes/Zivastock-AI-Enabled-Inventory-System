"""Add transparent inventory risk scores.

Revision ID: 008
Revises: 007
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inventory_risk_scores",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("location_id", sa.BigInteger(), nullable=True),
        sa.Column("calculation_date", sa.Date(), nullable=False),
        sa.Column("anomaly_score", sa.Numeric(precision=8, scale=4), nullable=False, server_default="0"),
        sa.Column("variance_score", sa.Numeric(precision=8, scale=4), nullable=False, server_default="0"),
        sa.Column("financial_value_score", sa.Numeric(precision=8, scale=4), nullable=False, server_default="0"),
        sa.Column("stockout_score", sa.Numeric(precision=8, scale=4), nullable=False, server_default="0"),
        sa.Column("adjustment_score", sa.Numeric(precision=8, scale=4), nullable=False, server_default="0"),
        sa.Column("accuracy_score", sa.Numeric(precision=8, scale=4), nullable=False, server_default="0"),
        sa.Column("criticality_score", sa.Numeric(precision=8, scale=4), nullable=False, server_default="0"),
        sa.Column("total_score", sa.Numeric(precision=8, scale=4), nullable=False, server_default="0"),
        sa.Column("risk_level", sa.String(length=20), nullable=False, server_default="LOW"),
        sa.Column("abc_class", sa.String(length=1), nullable=True),
        sa.Column("priority", sa.String(length=30), nullable=False, server_default="MONITOR"),
        sa.Column("explanation", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("calculation_version", sa.String(length=50), nullable=False, server_default="v1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("total_score >= 0 AND total_score <= 100", name="chk_inventory_risk_score_range"),
        sa.CheckConstraint("risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name="chk_inventory_risk_level"),
        sa.CheckConstraint("abc_class IS NULL OR abc_class IN ('A', 'B', 'C')", name="chk_inventory_risk_abc_class"),
    )
    for column in ("product_id", "location_id", "calculation_date", "total_score", "risk_level", "abc_class"):
        op.create_index(f"ix_inventory_risk_scores_{column}", "inventory_risk_scores", [column])


def downgrade() -> None:
    for column in ("abc_class", "risk_level", "total_score", "calculation_date", "location_id", "product_id"):
        op.drop_index(f"ix_inventory_risk_scores_{column}", table_name="inventory_risk_scores")
    op.drop_table("inventory_risk_scores")
