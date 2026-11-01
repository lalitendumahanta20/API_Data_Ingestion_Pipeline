import os
import time
import requests

from dotenv import load_dotenv

import logging

logger = logging.getLogger("ecommerce_pipeline")

# Load setting from env
load_dotenv()

# Read API Configuration
BASE_URL=os.getenv("API_BASE_URL")
API_TOKEN=os.getenv("API_TOKEN")

# Retry Configuration
MAX_RETRIES=int(os.getenv("API_MAX_RETRIES","3"))

BASE_DELAY=float(
    os.getenv("API_RETRY_BASE_DELAY","1")
)
REQUESTS_PER_SECOND = float(
    os.getenv("API_REQUESTS_PER_SECOND", "2")
)

if REQUESTS_PER_SECOND <= 0:
    raise ValueError("API_REQUESTS_PER_SECOND must be greater than zero")

if MAX_RETRIES < 0 or BASE_DELAY < 0:
    raise ValueError("Retry settings cannot be negative")

MIN_REQUEST_INTERVAL = 1 / REQUESTS_PER_SECOND

last_request_time = 0.0

# HTTP status codes that can be retried
RETRY_STATUS_CODES = {429,500,502,503,504}

# Check that configuration exists
if not BASE_URL:
    raise ValueError("API_BASE_URL is missing from .env")

if not API_TOKEN:
    raise ValueError("API_TOKEN is missing from .env")

# Create reuseable HTTP session
session=requests.Session()

# Add Authentication Header
session.headers.update({
    "X_API_Token": API_TOKEN,
    "Accept": "application/json"
})

# Rate Limitation Function

def apply_rate_limit():

    global last_request_time

    current_time = time.monotonic()

    elapsed_time = current_time - last_request_time

    wait_time = MIN_REQUEST_INTERVAL - elapsed_time

    if wait_time > 0:

        print(
            f"Rate limit: waiting {wait_time:.2f} seconds"
        )

        time.sleep(wait_time)

    last_request_time = time.monotonic()

# Retry Function
def fetch_page(endpoint,page,limit,extra_params=None):
    
    # Build API URL
    url = f"{BASE_URL}/{endpoint}"
    
    # Define Pagination Parameter
    params={
        "page": page,
        "limit": limit
    }
    
    # Add optional test parameters
    if extra_params:
        params.update(extra_params)
        
    # Initial request + configured retries
    for attempt in range(MAX_RETRIES + 1):
        apply_rate_limit()

        print(
            f"Requesting {endpoint}, page {page}, "
            f"attempt {attempt + 1}"
        )
        
        try:
            # Send Get Request to API
            response=session.get(
                url,
                params=params,
                timeout=30
            )
            
            logger.info(
                "API request: %s | Status: %s",
                endpoint,
                response.status_code
            )
                        
            # Check if HTTP Status ia retryable
            if response.status_code not in RETRY_STATUS_CODES:
                return response
            
            # If retries are exhausted, return final response
            if attempt == MAX_RETRIES:
                print("Maximum retries reached!")
                logger.error(
                    "Maximum retries reached for %s. HTTP status: %s",
                    endpoint,
                    response.status_code
                )
                return response
            logger.warning(
                "API request failed for %s. HTTP status: %s. Retry attempt: %s",
                endpoint,
                response.status_code,
                attempt + 1
            )
                        
            # Check Retry-After header
            retry_after=response.headers.get("Retry-After")
            
            if retry_after:
                try:
                    delay=float(retry_after)
                
                except ValueError:
                    delay=BASE_DELAY*(2**attempt)
            else:
                #Exponetial backoff
                delay=BASE_DELAY*(2**attempt)
                
            print(
                f"HTTP {response.status_code} received. "
                f"Retrying after {delay} seconds."
            )
            
            response.close()
            
            time.sleep(delay)
            
        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError
        ) as error:
            logger.warning(
                "Connection error for %s. Retry attempt: %s. Error: %s",
                endpoint,
                attempt + 1,
                error
            )
            if attempt==MAX_RETRIES:
                print("Maximum retries reached!")
                raise error
            
            delay=BASE_DELAY*(2**attempt)
            print(
                f"Temporary connection error: {error}"
            )
            print(
                f"Retrying after {delay} seconds."
            )
            
            time.sleep(delay)
            
    raise RuntimeError("Unexpected retry loop termination")