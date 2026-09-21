"""Add data-quality records and inventory feature snapshots.

Revision ID: 006
Revises: 005
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "data_quality_batches",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("import_batch_id", sa.BigInteger(), nullable=True),
        sa.Column("dataset_type", sa.String(length=50), nullable=False),
        sa.Column("source_system", sa.String(length=50), nullable=False),
        sa.Column("quality_score", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("total_records", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("valid_records", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("invalid_records", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duplicate_records", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("missing_value_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("issue_summary", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["import_batch_id"], ["imports.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("quality_score >= 0 AND quality_score <= 100", name="chk_quality_score_range"),
        sa.CheckConstraint("total_records >= 0", name="chk_quality_total_nonneg"),
        sa.CheckConstraint("valid_records >= 0 AND invalid_records >= 0", name="chk_quality_valid_invalid_nonneg"),
    )
    op.create_index("ix_data_quality_batches_import_batch_id", "data_quality_batches", ["import_batch_id"])

    op.create_table(
        "data_quality_issues",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("batch_id", sa.BigInteger(), nullable=False),
        sa.Column("record_reference", sa.String(length=150), nullable=True),
        sa.Column("row_number", sa.Integer(), nullable=True),
        sa.Column("issue_type", sa.String(length=50), nullable=False),
        sa.Column("field_name", sa.String(length=100), nullable=True),
        sa.Column("severity", sa.String(length=20), nullable=False, server_default="error"),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("raw_value", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("resolved", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("resolution_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["batch_id"], ["data_quality_batches.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("severity IN ('info', 'warning', 'error')", name="chk_quality_issue_severity"),
        sa.CheckConstraint("resolved IN ('open', 'resolved', 'ignored')", name="chk_quality_issue_status"),
    )
    op.create_index("ix_data_quality_issues_batch_id", "data_quality_issues", ["batch_id"])
    op.create_index("ix_data_quality_issues_record_reference", "data_quality_issues", ["record_reference"])
    op.create_index("ix_data_quality_issues_issue_type", "data_quality_issues", ["issue_type"])

    op.create_table(
        "inventory_feature_snapshots",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("location_id", sa.BigInteger(), nullable=True),
        sa.Column("feature_date", sa.Date(), nullable=False),
        sa.Column("lookback_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("feature_set_version", sa.String(length=50), nullable=False, server_default="v1"),
        sa.Column("current_quantity", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("average_quantity", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("minimum_quantity", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("maximum_quantity", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("daily_sales", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("weekly_sales", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("sales_velocity", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("demand_variability", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("sales_value", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("inventory_value", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("variance_quantity", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("variance_percentage", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("historical_variance", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("adjustment_frequency", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("count_disagreement", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("days_of_inventory", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("abc_class", sa.String(length=1), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "location_id", "feature_date", "feature_set_version", name="uq_inventory_feature_snapshot"),
    )
    op.create_index("ix_inventory_feature_snapshots_product_id", "inventory_feature_snapshots", ["product_id"])
    op.create_index("ix_inventory_feature_snapshots_location_id", "inventory_feature_snapshots", ["location_id"])
    op.create_index("ix_inventory_feature_snapshots_feature_date", "inventory_feature_snapshots", ["feature_date"])


def downgrade() -> None:
    op.drop_index("ix_inventory_feature_snapshots_feature_date", table_name="inventory_feature_snapshots")
    op.drop_index("ix_inventory_feature_snapshots_location_id", table_name="inventory_feature_snapshots")
    op.drop_index("ix_inventory_feature_snapshots_product_id", table_name="inventory_feature_snapshots")
    op.drop_table("inventory_feature_snapshots")
    op.drop_index("ix_data_quality_issues_issue_type", table_name="data_quality_issues")
    op.drop_index("ix_data_quality_issues_record_reference", table_name="data_quality_issues")
    op.drop_index("ix_data_quality_issues_batch_id", table_name="data_quality_issues")
    op.drop_table("data_quality_issues")
    op.drop_index("ix_data_quality_batches_import_batch_id", table_name="data_quality_batches")
    op.drop_table("data_quality_batches")
