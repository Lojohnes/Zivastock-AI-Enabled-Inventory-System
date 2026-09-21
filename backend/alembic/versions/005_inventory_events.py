"""Add the canonical inventory event model.

Revision ID: 005
Revises: 004
"""
from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "inventory_events" not in inspector.get_table_names():
        op.create_table(
            "inventory_events",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("product_id", sa.BigInteger(), nullable=False),
            sa.Column("location_id", sa.BigInteger(), nullable=True),
            sa.Column("event_type", sa.String(length=30), nullable=False),
            sa.Column("quantity", sa.Numeric(18, 4), nullable=False),
            sa.Column("unit_cost", sa.Numeric(18, 4), nullable=True),
            sa.Column("transaction_value", sa.Numeric(18, 4), nullable=True),
            sa.Column("event_timestamp", sa.DateTime(timezone=True), nullable=False),
            sa.Column("user_id", sa.BigInteger(), nullable=True),
            sa.Column("source_system", sa.String(length=50), nullable=False),
            sa.Column("source_record_id", sa.String(length=150), nullable=False),
            sa.Column("reference_number", sa.String(length=150), nullable=True),
            sa.Column("stocktake_session_id", sa.BigInteger(), nullable=True),
            sa.Column("import_batch_id", sa.BigInteger(), nullable=True),
            sa.Column("is_validated", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
            sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["stocktake_session_id"], ["stocktake_sessions.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["import_batch_id"], ["imports.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("source_system", "source_record_id", name="uq_inventory_event_source_record"),
            sa.CheckConstraint("event_type IN ('SALE', 'PURCHASE', 'RECEIPT', 'RETURN', 'TRANSFER', 'STOCKTAKE', 'COUNT', 'ADJUSTMENT', 'WASTE', 'DAMAGE', 'PRICE_CHANGE', 'LOCATION_CHANGE', 'OPENING_BALANCE', 'CLOSING_BALANCE')", name="chk_inventory_event_type"),
            sa.CheckConstraint("quantity >= 0", name="chk_inventory_event_quantity_nonneg"),
            sa.CheckConstraint("unit_cost IS NULL OR unit_cost >= 0", name="chk_inventory_event_unit_cost_nonneg"),
        )

    for name, column in (
        ("ix_inventory_events_product_id", "product_id"),
        ("ix_inventory_events_location_id", "location_id"),
        ("ix_inventory_events_event_type", "event_type"),
        ("ix_inventory_events_event_timestamp", "event_timestamp"),
        ("ix_inventory_events_source_system", "source_system"),
        ("ix_inventory_events_user_id", "user_id"),
        ("ix_inventory_events_reference_number", "reference_number"),
        ("ix_inventory_events_stocktake_session_id", "stocktake_session_id"),
        ("ix_inventory_events_import_batch_id", "import_batch_id"),
    ):
        op.execute(sa.text(f"CREATE INDEX IF NOT EXISTS {name} ON inventory_events ({column})"))

    op.execute("ALTER TABLE imports DROP CONSTRAINT IF EXISTS imports_entity_type_check")
    op.execute("ALTER TABLE imports DROP CONSTRAINT IF EXISTS chk_imports_entity_type")
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE imports ADD CONSTRAINT chk_imports_entity_type
            CHECK (entity_type IN ('products', 'locations', 'users', 'counts', 'categories', 'inventory_events'));
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE imports DROP CONSTRAINT IF EXISTS chk_imports_entity_type")
    op.execute("""
        ALTER TABLE imports ADD CONSTRAINT chk_imports_entity_type
        CHECK (entity_type IN ('products', 'locations', 'users', 'counts', 'categories'))
    """)
    op.execute("DROP TABLE IF EXISTS inventory_events")
