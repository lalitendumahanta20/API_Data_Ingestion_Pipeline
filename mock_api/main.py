from fastapi import FastAPI, Header, HTTPException, Query
from typing import Optional
from datetime import datetime,timezone
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load enviromental variables
load_dotenv()

# Intialize FastAPI Application
app=FastAPI(
    title="E-Commerce Mock API",
    description="Mock API for Data Engineering ingestion project",
    version="1.0.0"
)

# API authentication Token
API_TOKEN=os.getenv("API_TOKEN", "test-token")


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "sample_data"

def load_json_data(filename):
    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Sample data file not found: {file_path}"
        )

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)
    
customers = load_json_data("customers.json")
orders = load_json_data("orders.json")

print(f"Loaded {len(customers)} customers")
print(f"Loaded {len(orders)} orders")


# 3.Failure Simulation Tracker
failure_tracker=set()

# 4.Authentication Function
def verify_token(x_api_token: Optional[str]):
    expected_token=API_TOKEN
    
    if x_api_token != expected_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Token"
        )
        
# 5. Reusable Pagination Function
def paginate_records(records,page,limit,updated_since):
    
    # Increament Date Filtering
    if updated_since:
        try:
            filter_date=datetime.fromisoformat(
                updated_since.replace("Z","+00:00")
            )
            
            filtered_records=[]
            
            for record in records:
                record_date=datetime.fromisoformat(
                    record["updated_at"].replace("Z","+00:00")
                )
                
                if record_date >= filter_date:
                    filtered_records.append(record)
                    
            records=filtered_records
            
        except (ValueError,TypeError,KeyError):
            raise HTTPException(
                status_code=400,
                detail="Invalid updated_since timestamp"
            )
            
    # Calculate Paginated Index
    total=len(records)
    
    start=  (page - 1) * limit
    
    end=start+limit
    
    # Get Requested Record
    page_data=records[start:end]
    
    # Check Next Page
    has_next=end < total
    
    return {
        "data":page_data,
        "page":page,
        "limit":limit,
        "total":total,
        "has_next":has_next,
        "next_page":page + 1 if has_next else None
    }
    
    
# 6. Health Check API
@app.get("/")
def home():
    return {
        "message":"E-Commerce Mock API is running",
        "status":"Healthy"
    }
    
# 7. Customer API
@app.get("/customers")
def get_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(2, ge=1, le=1000),
    updated_since: Optional[str] = None,
    x_api_token: Optional[str] = Header(None,alias="X_API_Token")
):
    verify_token(x_api_token)
    
    return paginate_records(customers,page,limit,updated_since)

# 8. Orders API 
@app.get("/orders")
def get_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(2, ge=1, le=1000),
    updated_since: Optional[str] = None,
    fail_first: bool = False,
    x_api_token: Optional[str] = Header(None, alias="X_API_Token")
):
    verify_token(x_api_token)
    
    # Simulate One temporary server failure
    failure_key=("orders","500")
    
    if fail_first and failure_key not in failure_tracker:
        failure_tracker.add(failure_key)
        
        raise HTTPException(
            status_code=500,
            detail="Simulated temporary server failure"
        )
        
    return paginate_records(orders,page,limit,updated_since)

