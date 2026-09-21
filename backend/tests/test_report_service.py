from sqlalchemy.orm import Session

from app.models.location import Location, Shelf, ShelfSection
from app.models.product import Product
from app.models.role import Role
from app.models.session import StocktakeSession
from app.models.user import User
from app.schemas.count import FirstCountCreate
from app.services.count_service import CountService
from app.services.report_service import ReportService


def seed_data(session: Session):
    role = Role(name="Counter", description="Stock counter")
    session.add(role)
    session.flush()

    user = User(
        email="counter@example.com",
        password_hash="secret",
        first_name="Test",
        last_name="Counter",
        role_id=role.id,
        is_active=True,
    )
    product = Product(
        barcode="123456",
        product_code="P001",
        description="Test Product",
        unit_of_measure="EA",
        system_quantity=100.0,
        unit_cost=10.0,
    )
    location = Location(name="Warehouse", type="warehouse")
    session.add_all([user, product, location])
    session.flush()

    shelf = Shelf(name="Shelf A", location_id=location.id)
    session.add(shelf)
    session.flush()

    section = ShelfSection(name="A1", shelf_id=shelf.id)
    session.add(section)
    session.flush()

    stock_session = StocktakeSession(
        name="Cycle 1",
        description="Test cycle",
        location_id=location.id,
        created_by=user.id,
    )
    session.add(stock_session)
    session.commit()

    CountService(session).create_first_count(
        FirstCountCreate(
            product_id=product.id,
            shelf_section_id=section.id,
            quantity=95,
            session_id=stock_session.id,
            source="web",
        ),
        user.id,
    )
    return user, product, section, stock_session


def test_get_dashboard_stats(db_session, monkeypatch):
    seed_data(db_session)
    monkeypatch.setattr(ReportService, "get_session_progress", lambda self: [])
    stats = ReportService(db_session).get_dashboard_stats()

    assert stats["summary"]["total_sessions"] == 1
    assert stats["summary"]["total_products"] == 1
    assert stats["summary"]["total_first_counts"] == 1


def test_generate_variance_report(db_session):
    _, _, _, stock_session = seed_data(db_session)
    result = ReportService(db_session).generate_variance_report(stock_session.id)

    assert result["session_id"] == stock_session.id
    assert len(result["variances"]) == 1
    assert result["variances"][0]["variance_quantity"] == -5.0
    assert result["variances"][0]["variance_value"] == -50.0


def test_generate_missing_stock_report(db_session):
    _, _, _, stock_session = seed_data(db_session)
    result = ReportService(db_session).generate_missing_stock_report(stock_session.id)

    assert result["total_products"] == 1
    assert result["counted_products"] == 1
    assert result["missing_products"] == 0
