"""Add explainable AI recommendations and human decisions.

Revision ID: 010
Revises: 009
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    json_type = lambda: postgresql.JSONB(astext_type=sa.Text())
    op.create_table(
        "ai_recommendations",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("location_id", sa.BigInteger(), nullable=True),
        sa.Column("recommendation_type", sa.String(length=40), nullable=False),
        sa.Column("recommendation_text", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(length=30), nullable=False, server_default="MONITOR"),
        sa.Column("confidence_score", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("evidence", json_type(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("expected_impact", json_type(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("model_version_id", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["model_version_id"], ["model_versions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("status IN ('PENDING', 'APPROVED', 'REJECTED', 'OVERRIDDEN', 'COMPLETED', 'EXPIRED')", name="chk_recommendation_status"),
        sa.CheckConstraint("confidence_score IS NULL OR confidence_score BETWEEN 0 AND 100", name="chk_recommendation_confidence"),
    )
    for column in ("product_id", "location_id", "recommendation_type", "priority", "status"):
        op.create_index(f"ix_ai_recommendations_{column}", "ai_recommendations", [column])

    op.create_table(
        "recommendation_decisions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("recommendation_id", sa.BigInteger(), nullable=False),
        sa.Column("decision", sa.String(length=20), nullable=False),
        sa.Column("decided_by", sa.BigInteger(), nullable=True),
        sa.Column("decision_reason", sa.Text(), nullable=True),
        sa.Column("override_flag", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["recommendation_id"], ["ai_recommendations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["decided_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("decision IN ('APPROVED', 'REJECTED', 'OVERRIDDEN')", name="chk_recommendation_decision"),
        sa.CheckConstraint("override_flag IN (0, 1)", name="chk_recommendation_override"),
    )
    op.create_index("ix_recommendation_decisions_recommendation_id", "recommendation_decisions", ["recommendation_id"])

    op.create_table(
        "recommendation_outcomes",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("recommendation_id", sa.BigInteger(), nullable=False),
        sa.Column("actual_action", sa.String(length=100), nullable=True),
        sa.Column("outcome_status", sa.String(length=30), nullable=False),
        sa.Column("actual_result", sa.Text(), nullable=True),
        sa.Column("variance_after_action", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("stockout_avoided", sa.Integer(), nullable=True),
        sa.Column("recorded_by", sa.BigInteger(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["recommendation_id"], ["ai_recommendations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recorded_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("outcome_status IN ('PENDING', 'SUCCESS', 'PARTIAL', 'FAILED', 'NOT_APPLICABLE')", name="chk_recommendation_outcome"),
        sa.CheckConstraint("stockout_avoided IS NULL OR stockout_avoided IN (0, 1)", name="chk_stockout_avoided"),
    )
    op.create_index("ix_recommendation_outcomes_recommendation_id", "recommendation_outcomes", ["recommendation_id"])


def downgrade() -> None:
    op.drop_index("ix_recommendation_outcomes_recommendation_id", table_name="recommendation_outcomes")
    op.drop_table("recommendation_outcomes")
    op.drop_index("ix_recommendation_decisions_recommendation_id", table_name="recommendation_decisions")
    op.drop_table("recommendation_decisions")
    for column in ("status", "priority", "recommendation_type", "location_id", "product_id"):
        op.drop_index(f"ix_ai_recommendations_{column}", table_name="ai_recommendations")
    op.drop_table("ai_recommendations")
