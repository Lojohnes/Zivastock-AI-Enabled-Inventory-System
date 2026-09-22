"""Add analysis-run scoping for Command Centre results.

Revision ID: 011
Revises: 010
"""
from alembic import op
import sqlalchemy as sa

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None

DERIVED_TABLES = (
    "anomaly_results",
    "inventory_risk_scores",
    "forecast_results",
    "inventory_exposures",
    "ai_recommendations",
)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "analysis_runs" not in inspector.get_table_names():
        op.create_table(
            "analysis_runs",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("analysis_key", sa.String(length=100), nullable=False),
            sa.Column("analysis_type", sa.String(length=30), nullable=False),
            sa.Column("reference_id", sa.String(length=100), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="COMPLETED"),
            sa.Column("created_by", sa.BigInteger(), nullable=True),
            sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("analysis_key"),
            sa.CheckConstraint("status IN ('RUNNING', 'COMPLETED', 'FAILED')", name="chk_analysis_run_status"),
        )
    for name, column in (
        ("ix_analysis_runs_analysis_key", "analysis_key"),
        ("ix_analysis_runs_analysis_type", "analysis_type"),
        ("ix_analysis_runs_reference_id", "reference_id"),
        ("ix_analysis_runs_started_at", "started_at"),
    ):
        op.execute(sa.text(f"CREATE INDEX IF NOT EXISTS {name} ON analysis_runs ({column})"))

    for table in DERIVED_TABLES:
        op.execute(sa.text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS analysis_key VARCHAR(100)"))
        op.execute(sa.text(f"CREATE INDEX IF NOT EXISTS ix_{table}_analysis_key ON {table} (analysis_key)"))


def downgrade() -> None:
    for table in reversed(DERIVED_TABLES):
        op.execute(sa.text(f"DROP INDEX IF EXISTS ix_{table}_analysis_key"))
        op.execute(sa.text(f"ALTER TABLE {table} DROP COLUMN IF EXISTS analysis_key"))
    op.execute(sa.text("DROP TABLE IF EXISTS analysis_runs"))
