"""Add model registry and anomaly detection results.

Revision ID: 007
Revises: 006
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


_JSON = lambda: postgresql.JSONB(astext_type=sa.Text())


def upgrade() -> None:
    op.create_table(
        "model_versions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("algorithm", sa.String(length=100), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("dataset_version", sa.String(length=100), nullable=True),
        sa.Column("feature_set_version", sa.String(length=100), nullable=True),
        sa.Column("features", _JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("hyperparameters", _JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("training_start", sa.Date(), nullable=True),
        sa.Column("training_end", sa.Date(), nullable=True),
        sa.Column("evaluation_metrics", _JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("artifact_path", sa.String(length=512), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="evaluated"),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("status IN ('draft', 'trained', 'evaluated', 'selected', 'retired')", name="chk_model_version_status"),
    )
    op.create_index("ix_model_versions_model_name", "model_versions", ["model_name"])
    op.create_index("ix_model_versions_status", "model_versions", ["status"])

    op.create_table(
        "anomaly_results",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("location_id", sa.BigInteger(), nullable=True),
        sa.Column("feature_date", sa.Date(), nullable=False),
        sa.Column("model_version_id", sa.BigInteger(), nullable=True),
        sa.Column("algorithm", sa.String(length=100), nullable=False),
        sa.Column("anomaly_flag", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("anomaly_score", sa.Numeric(precision=8, scale=4), nullable=False, server_default="0"),
        sa.Column("risk_level", sa.String(length=20), nullable=False, server_default="LOW"),
        sa.Column("threshold_used", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("evidence", _JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("feature_contributions", _JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["model_version_id"], ["model_versions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("anomaly_flag IN (0, 1)", name="chk_anomaly_flag"),
        sa.CheckConstraint("anomaly_score >= 0 AND anomaly_score <= 100", name="chk_anomaly_score_range"),
        sa.CheckConstraint("risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name="chk_anomaly_risk_level"),
    )
    for column in ("product_id", "location_id", "feature_date", "model_version_id"):
        op.create_index(f"ix_anomaly_results_{column}", "anomaly_results", [column])


def downgrade() -> None:
    for column in ("model_version_id", "feature_date", "location_id", "product_id"):
        op.drop_index(f"ix_anomaly_results_{column}", table_name="anomaly_results")
    op.drop_table("anomaly_results")
    op.drop_index("ix_model_versions_status", table_name="model_versions")
    op.drop_index("ix_model_versions_model_name", table_name="model_versions")
    op.drop_table("model_versions")
