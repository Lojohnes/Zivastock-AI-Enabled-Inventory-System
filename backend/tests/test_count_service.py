import pytest
from sqlalchemy.orm import Session

from app.models.location import Location, Shelf, ShelfSection
from app.models.product import Product
from app.models.role import Role
from app.models.session import StocktakeSession
from app.models.user import User
from app.schemas.count import FirstCountCreate
from app.services.count_service import CountService


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
    location = Location(name="Warehouse", type="warehouse", address="Main warehouse")
    session.add_all([user, location])
    session.flush()

    shelf = Shelf(name="Shelf A", location_id=location.id)
    session.add(shelf)
    session.flush()

    section = ShelfSection(name="A1", shelf_id=shelf.id)
    product = Product(
        barcode="123456",
        product_code="P001",
        description="Test Product",
        unit_of_measure="EA",
        system_quantity=100.0,
        unit_cost=10.0,
    )
    session.add_all([section, product])
    session.flush()

    stock_session = StocktakeSession(
        name="Cycle 1",
        location_id=location.id,
        created_by=user.id,
    )
    session.add(stock_session)
    session.commit()
    return user, product, section, stock_session


def create_first_count(service, product, section, stock_session, user, quantity=95):
    return service.create_first_count(
        FirstCountCreate(
            product_id=product.id,
            shelf_section_id=section.id,
            quantity=quantity,
            session_id=stock_session.id,
            source="web",
        ),
        user.id,
    )


def test_create_and_get_first_count(db_session):
    user, product, section, stock_session = seed_data(db_session)
    service = CountService(db_session)

    count = create_first_count(service, product, section, stock_session, user)
    counts, total = service.get_first_counts(session_id=stock_session.id)

    assert count.product_id == product.id
    assert count.shelf_section_id == section.id
    assert float(count.quantity) == 95.0
    assert total == 1
    assert len(counts) == 1


def test_create_first_count_product_not_found(db_session):
    user, _, section, stock_session = seed_data(db_session)
    service = CountService(db_session)

    with pytest.raises(ValueError, match="Product not found"):
        service.create_first_count(
            FirstCountCreate(
                product_id=9999,
                shelf_section_id=section.id,
                quantity=95,
                session_id=stock_session.id,
                source="web",
            ),
            user.id,
        )


def test_delete_first_count(db_session):
    user, product, section, stock_session = seed_data(db_session)
    service = CountService(db_session)
    count = create_first_count(service, product, section, stock_session, user)

    assert service.delete_first_count(count.id) is True
    assert service.delete_first_count(count.id) is False
