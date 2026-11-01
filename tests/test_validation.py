
import pytest

from transformation.validation import (
    is_positive_integer,
    is_valid_timestamp,
    is_valid_email,
    validate_customer,
    validate_order
)

# 1. Test positive integer function

def test_positive_integer_valid():
    assert is_positive_integer(10) is True


def test_positive_integer_zero():
    assert is_positive_integer(0) is False


def test_positive_integer_negative():
    assert is_positive_integer(-5) is False


def test_positive_integer_rejects_boolean():
    assert is_positive_integer(True) is False


def test_positive_integer_rejects_string():
    assert is_positive_integer("10") is False


# 2. Test timestamp validation

def test_valid_timestamp():
    assert is_valid_timestamp("2026-11-01T10:30:00Z") is True


def test_timestamp_without_timezone():
    assert is_valid_timestamp("2026-11-01T10:30:00") is False


def test_invalid_timestamp():
    assert is_valid_timestamp("invalid-date") is False


def test_timestamp_with_wrong_type():
    assert is_valid_timestamp(12345) is False


# 3. Test email validation

def test_valid_email():
    assert is_valid_email("test@example.com") is True


def test_invalid_email_without_at():
    assert is_valid_email("testexample.com") is False


def test_invalid_email_without_domain():
    assert is_valid_email("test@") is False


def test_invalid_email_without_dot():
    assert is_valid_email("test@example") is False


# 4. Test customer validation

def valid_customer():
    return {
        "customer_id": 1,
        "customer_name": "John",
        "email": "john@example.com",
        "created_at": "2026-11-01T10:00:00Z",
        "updated_at": "2026-11-01T10:30:00Z"
    }


def test_valid_customer():
    record = valid_customer()

    errors = validate_customer(record)

    assert errors == []


def test_customer_empty_name():
    record = valid_customer()
    record["customer_name"] = ""

    errors = validate_customer(record)

    assert "customer_name cannot be empty" in errors


def test_customer_invalid_email():
    record = valid_customer()
    record["email"] = "invalid-email"

    errors = validate_customer(record)

    assert "email format is invalid" in errors


def test_customer_invalid_id():
    record = valid_customer()
    record["customer_id"] = -1

    errors = validate_customer(record)

    assert "customer_id must be a positive integer" in errors


def test_customer_invalid_record_type():
    errors = validate_customer("invalid")

    assert errors == ["Customer record must be a JSON object"]

# 5. Test order validation

class MockCursor:

    def __init__(self, customer_exists=True):
        self.customer_exists = customer_exists
        self.executed_query = None
        self.executed_params = None

    def execute(self, query, *params):
        self.executed_query = query
        self.executed_params = params

    def fetchone(self):
        if self.customer_exists:
            return (1,)

        return None


def valid_order():
    return {
        "order_id": 101,
        "customer_id": 1,
        "order_amount": 500.0,
        "order_status": "COMPLETED",
        "created_at": "2026-11-01T10:00:00Z",
        "updated_at": "2026-11-01T10:30:00Z"
    }


def test_valid_order():
    record = valid_order()
    cursor = MockCursor(customer_exists=True)

    errors = validate_order(record, cursor)

    assert errors == []


def test_order_negative_amount():
    record = valid_order()
    record["order_amount"] = -100

    cursor = MockCursor()

    errors = validate_order(record, cursor)

    assert (
        "order_amount must be a finite, non-negative number"
        in errors
    )


def test_order_invalid_status():
    record = valid_order()
    record["order_status"] = "INVALID"

    cursor = MockCursor()

    errors = validate_order(record, cursor)

    assert "order_status is invalid" in errors


def test_order_customer_does_not_exist():
    record = valid_order()
    cursor = MockCursor(customer_exists=False)

    errors = validate_order(record, cursor)

    assert "customer_id 1 does not exist" in errors


def test_order_invalid_record_type():
    cursor = MockCursor()

    errors = validate_order("invalid", cursor)

    assert errors == ["Order record must be a JSON object"]
