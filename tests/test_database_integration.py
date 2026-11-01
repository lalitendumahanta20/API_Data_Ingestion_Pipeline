
import uuid
import pytest

from storage.database import get_connection
from ingestion.ingest import insert_customers, insert_orders


@pytest.fixture
def db_cursor():
    """Connect to SQL Server and roll back test changes afterward."""
    connection = get_connection()
    cursor = connection.cursor()

    try:
        yield cursor
    finally:
        connection.rollback()
        cursor.close()
        connection.close()


def create_customer():
    return {
        "customer_id": 1_000_000_000 + uuid.uuid4().int % 1_000_000_000,
        "customer_name": "Integration Test Customer",
        "email": f"test_{uuid.uuid4().hex[:12]}@example.com",
        "created_at": "2026-11-01T10:00:00Z",
        "updated_at": "2026-11-01T10:00:00Z"
    }


# Test 1: Verify SQL Server connection
def test_database_connection(db_cursor):
    db_cursor.execute("SELECT 1")
    result = db_cursor.fetchone()

    assert result[0] == 1


# Test 2: Customer insert, duplicate handling, and update
def test_customer_insert_and_upsert(db_cursor):
    customer = create_customer()

    # First execution: insert new customer
    inserted, updated = insert_customers(db_cursor, [customer])

    assert inserted == 1
    assert updated == 0

    # Second execution: same data should not create another record
    inserted, updated = insert_customers(db_cursor, [customer])

    assert inserted == 0
    assert updated == 0

    # Third execution: newer data should update the customer
    updated_customer = customer.copy()
    updated_customer["customer_name"] = "Updated Integration Customer"
    updated_customer["updated_at"] = "2026-11-01T10:30:00Z"

    inserted, updated = insert_customers(
        db_cursor, [updated_customer]
    )

    assert inserted == 0
    assert updated == 1

    db_cursor.execute(
        """
        SELECT customer_name
        FROM dbo.customers
        WHERE customer_id = ?
        """,
        customer["customer_id"]
    )

    result = db_cursor.fetchone()

    assert result[0] == "Updated Integration Customer"


# Test 3: Order insert, duplicate handling, and update
def test_order_insert_and_upsert(db_cursor):
    customer = create_customer()

    # Create the parent customer first
    inserted, updated = insert_customers(db_cursor, [customer])

    assert inserted == 1
    assert updated == 0

    order = {
        "order_id": 1_000_000_000 + uuid.uuid4().int % 1_000_000_000,
        "customer_id": customer["customer_id"],
        "order_amount": 500.00,
        "order_status": "PENDING",
        "created_at": "2026-11-01T10:00:00Z",
        "updated_at": "2026-11-01T10:00:00Z"
    }

    # First execution: insert order
    inserted, updated = insert_orders(db_cursor, [order])

    assert inserted == 1
    assert updated == 0

    # Second execution: unchanged order should not be updated
    inserted, updated = insert_orders(db_cursor, [order])

    assert inserted == 0
    assert updated == 0

    # Third execution: newer data should update the order
    updated_order = order.copy()
    updated_order["order_amount"] = 750.00
    updated_order["order_status"] = "COMPLETED"
    updated_order["updated_at"] = "2026-11-01T10:30:00Z"

    inserted, updated = insert_orders(
        db_cursor, [updated_order]
    )

    assert inserted == 0
    assert updated == 1

    db_cursor.execute(
        """
        SELECT order_amount, order_status
        FROM dbo.orders
        WHERE order_id = ?
        """,
        order["order_id"]
    )

    result = db_cursor.fetchone()

    assert float(result[0]) == 750.00
    assert result[1] == "COMPLETED"
