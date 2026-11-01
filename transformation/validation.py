import re
import math
from datetime import datetime

# Common Validation Function
def is_positive_integer(value):
    
    # bool is a subclass of int in Python
    # so explicitly reject True and False.
    return (
        isinstance(value,int)
        and not isinstance(value,bool)
        and value > 0
    )
    
def is_valid_timestamp(value):
    if not isinstance(value,str):
        return False
    
    try:
        parsed_date=datetime.fromisoformat(
            value.replace("Z","+00:00")
        )
        
        # Require a timezone-aware timestamp
        return parsed_date.tzinfo is not None
    
    except ValueError:
        return False
    
def is_valid_email(email):
    if not isinstance(email,str):
        return False
    
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    
    return re.match(pattern,email) is not None

# CUSTOMER VALIDATION

def validate_customer(record):
    errors=[]
    
    if not isinstance(record,dict):
        return ["Customer record must be a JSON object"]
    
    customer_id = record.get("customer_id")
    customer_name = record.get("customer_name")
    email = record.get("email")
    created_at = record.get("created_at")
    updated_at = record.get("updated_at")
    
    if not is_positive_integer(customer_id):
        errors.append("customer_id must be a positive integer")
        
    if not isinstance(customer_name,str) or not customer_name.strip():
        errors.append("customer_name cannot be empty")
        
    if not is_valid_email(email):
        errors.append("email format is invalid")
        
    if not is_valid_timestamp(created_at):
        errors.append("created_at must be a valid timezone-aware timestamp")
        
    if not is_valid_timestamp(updated_at):
        errors.append("updated_at must be a valid timezone-aware timestamp")
        
    return errors

# Order Validation
def validate_order(record,cursor):
    errors=[]
    
    if not isinstance(record,dict):
        return ["Order record must be a JSON object"]
    
    order_id = record.get("order_id")
    customer_id = record.get("customer_id")
    amount = record.get("order_amount")
    status = record.get("order_status")
    created_at = record.get("created_at")
    updated_at = record.get("updated_at")
    
    if not is_positive_integer(order_id):
        errors.append("order_id must be a positive integer")
        
    if not is_positive_integer(customer_id):
        errors.append("customer_id must be a positive integer")
        
    if (
        isinstance(amount,bool)
        or not isinstance(amount,(int,float))
        or not math.isfinite(amount)
        or amount < 0
    ):
        errors.append("order_amount must be a finite, non-negative number")
        
    allowed_statuses={
        "COMPLETED","PENDING","CANCELLED"
    }
    
    if (
        not isinstance(status,str)
        or status not in allowed_statuses
    ):
        errors.append("order_status is invalid")
        
    if not is_valid_timestamp(created_at):
        errors.append("created_at must be a valid timezone-aware timestamp")
        
    if not is_valid_timestamp(updated_at):
        errors.append("updated_at must be a valid timezone-aware timestamp")
        
    # Check whether the customer exists
    if is_positive_integer(customer_id):
        cursor.execute(
            """
            select 1 from customers
            where customer_id=?
            """,
            customer_id
        )
        if cursor.fetchone() is None:
            errors.append(f"customer_id {customer_id} does not exist")
    return errors
