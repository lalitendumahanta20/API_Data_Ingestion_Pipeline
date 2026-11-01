# Reliable E-Commerce API Data Ingestion Pipeline

## 1. Project Overview

The **Reliable E-Commerce API Data Ingestion Pipeline** is a Python-based ETL project designed to extract customer and order data from REST APIs, validate and transform the records, and load them into a SQL Server database.

The pipeline is designed with reliability and data quality in mind. It supports paginated API extraction, incremental data loading, duplicate prevention through upsert operations, invalid-record quarantine, checkpoint management, logging, and failure handling.

A FastAPI-based mock API is included to simulate a real-world e-commerce API environment.

## 2. Project Objectives

- Extract customer and order data from REST APIs.
- Handle API pagination efficiently.
- Support incremental data ingestion using timestamps.
- Validate incoming records before database insertion.
- Store invalid records in a quarantine table.
- Prevent duplicate records using insert and update (upsert) logic.
- Maintain ingestion checkpoints for incremental processing.
- Capture raw API responses for traceability.
- Handle API failures and database errors.
- Generate sample datasets for testing and performance evaluation.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Mock REST API |
| Requests | API communication |
| SQL Server | Database storage |
| SQLAlchemy / pyodbc | Database connectivity |
| Pandas | Data analysis and processing |
| Python-dotenv | Environment variable management |
| Pytest | Automated testing |
| Logging | Pipeline monitoring and debugging |

## 4. Project Structure

```text
API_Data_Ingestion_Pipeline/
│
├── ingestion/
│   ├── __init__.py
│   ├── api_client.py
│   ├── ingest.py
│   └── logging_config.py
│
├── mock_api/
│   ├── __init__.py
│   └── main.py
│
├── storage/
│   ├── database.py
│   ├── Ecommerce_Pipeline.sql
│   └── reports.sql
│
├── transformation/
│   ├── __init__.py
│   └── validation.py
│
├── scripts/
│   └── generate_data.py
│
├── sample_data/
│   ├── customers.json
│   └── orders.json
│
├── tests/
│   ├── test_api_client.py
│   ├── test_database_integration.py
│   ├── test_failure_handling.py
│   └── test_validation.py
│
├── docs/
│   ├── data_dictionary.md
│   └── design_decisions.md
│
├── logs/
│
├── .env
├── .env.example
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

## 5. Key Features

### 5.1 API Data Extraction

The pipeline extracts customer and order records from REST API endpoints.

- Customer endpoint: `/customers`
- Order endpoint: `/orders`
- API authentication using an API token.
- Configurable page size.
- Pagination support.
- Incremental extraction using `updated_since`.

### 5.2 Pagination Handling

The API returns data in multiple pages instead of sending all records in one response.

The ingestion process reads the `next_page` value and continues fetching records until all available pages have been processed.

### 5.3 Data Validation

Incoming records are validated before loading into the database.

**Customer validation:**
- Customer ID must be a positive integer.
- Customer name must not be empty.
- Email must have a valid format.
- Created and updated timestamps must be valid timezone-aware timestamps.

**Order validation:**
- Order ID must be a positive integer.
- Customer ID must be valid.
- Order amount must be a finite, non-negative number.
- Order status must be one of the allowed values: `COMPLETED`, `PENDING`, or `CANCELLED`.
- Customer ID must exist in the customers table.

### 5.4 Invalid Record Quarantine

Records that fail validation are not inserted into the main business tables.

Instead, they are stored in a quarantine table with:
- Original record data.
- Validation failure reason.
- Related entity information.

This helps maintain data quality while preserving rejected records for investigation.

### 5.5 Upsert Logic

The pipeline uses insert-or-update logic to prevent duplicate records.

- If a record does not exist, it is inserted.
- If a record already exists and the incoming `updated_at` timestamp is newer, the existing record is updated.
- If the incoming record is not newer, the existing record is retained.

### 5.6 Incremental Data Loading

The pipeline maintains checkpoints to track the last processed update timestamp.

On subsequent runs, the API is queried using the saved checkpoint so that only records updated since the previous checkpoint are requested.

### 5.7 Raw API Response Storage

Raw API responses are stored in the database for traceability and debugging.

This helps investigate source data issues and understand what was received from the API.

### 5.8 Logging and Failure Handling

The pipeline uses Python logging to track:
- Pipeline start and completion.
- Run ID.
- API requests.
- Records fetched and processed.
- Inserted and updated records.
- Rejected records.
- API and database failures.

Pipeline execution status is recorded as `SUCCESS` or `FAILED`.

### 5.9 Sample Data Generation

The project includes a data generation script to create larger datasets for testing.

The script generates:
- Customer JSON records.
- Order JSON records.
- Randomized order amounts and statuses.
- Timestamp fields.
- Reproducible sample data using a random seed.

## 6. Database Design

The SQL Server database contains tables for managing business data and pipeline execution.

| Table | Purpose |
|---|---|
| customers | Stores customer information |
| orders | Stores customer order information |
| raw_api_responses | Stores raw API responses |
| quarantine_records | Stores invalid records and rejection reasons |
| checkpoints | Stores incremental ingestion checkpoints |
| pipeline_runs | Tracks pipeline execution status and metrics |

The orders table maintains a relationship with the customers table through `customer_id`.

**Note:** Execute the database creation SQL script before running the ingestion pipeline.

## 7. Installation and Setup

### Step 1: Clone the repository

```bash
git clone <your-github-repository-url>
cd API_Data_Ingestion_Pipeline
```

### Step 2: Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure environment variables

Create a `.env` file in the project root.

Add the API and database configuration required by your application.

Example:

```env
API_BASE_URL=http://127.0.0.1:8000
API_TOKEN=test-token
API_PAGE_LIMIT=100

# Add your SQL Server connection settings here.
# Use the exact variable names expected by storage/database.py.
```

Do not upload your actual `.env` file to GitHub.

### Step 5: Configure SQL Server

1. Open SQL Server Management Studio (SSMS).
2. Connect to your SQL Server instance.
3. Open `storage/Ecommerce_Pipeline.sql`.
4. Execute the SQL script.
5. Verify that the required database tables have been created.
6. Configure your database connection in `.env`.

## 8. Generate Sample Data

Run the following command from the project root:

```bash
python scripts/generate_data.py --count 1000 --seed 42
```

This generates:

- 1,000 customer records.
- 2,000 order records.

Generated files are saved inside the `sample_data/` directory.

You can change the number of customers using the `--count` argument.

Example:

```bash
python scripts/generate_data.py --count 5000 --seed 42
```

## 9. Run the Mock API

Start the FastAPI server:

```bash
python -m uvicorn mock_api.main:app --reload
```

Open the API documentation:

http://127.0.0.1:8000/docs

Available endpoints:

```text
GET /
GET /customers
GET /orders
```

The mock API supports authentication, pagination, incremental filtering, and simulated API failure handling.

## 10. Run the Ingestion Pipeline

Keep the mock API running in the first terminal.

Open a second terminal, activate the virtual environment, and execute:

```bash
python -m ingestion.ingest
```

The pipeline performs the following operations:

1. Starts a new pipeline run.
2. Connects to the SQL Server database.
3. Fetches customer data from the API.
4. Validates customer records.
5. Inserts or updates valid customer records.
6. Quarantines invalid customer records.
7. Fetches order data from the API.
8. Validates order records and customer references.
9. Inserts or updates valid order records.
10. Quarantines invalid order records.
11. Saves ingestion checkpoints.
12. Updates pipeline execution status.
13. Logs execution metrics.

## 11. Run Automated Tests

Execute all tests from the project root:

```bash
python -m pytest -v
```
Run a specific test file:
```bash
pytest tests/test_api_client.py -v
```
Run validation tests:
```bash
pytest tests/test_validation.py -v
```
Run database integration tests:
```bash
pytest tests/test_database_integration.py -v
```
Run failure handling tests:
```bash
pytest tests/test_failure_handling.py -v
```
The test suite covers:

- API client functionality.
- Data validation.
- Database integration.
- Failure handling.

## 12. Verify Database Results

Use SQL Server Management Studio to verify the ingested data.

Check customer records:

```sql
SELECT COUNT(*) AS TotalCustomers
FROM customers;
```

Check order records:

```sql
SELECT COUNT(*) AS TotalOrders
FROM orders;
```

Check quarantined records:

```sql
SELECT *
FROM quarantine_records;
```

Check pipeline execution:

```sql
SELECT *
FROM pipeline_runs
ORDER BY start_time DESC;
```

Check ingestion checkpoints:

```sql
SELECT *
FROM checkpoints;
```

Use `storage/reports.sql` for additional reporting queries.

## 13. Reliability and Design Considerations

The pipeline includes several reliability features:

- API authentication.
- Pagination handling.
- Incremental data extraction.
- Record-level validation.
- Invalid-record quarantine.
- Upsert-based duplicate prevention.
- Raw response storage.
- Checkpoint tracking.
- Pipeline execution logging.
- Failure simulation and automated tests.

**Important improvement area:** Checkpoint advancement should account for rejected records. If a rejected record's timestamp is included in the saved checkpoint, it may not be fetched again during the next incremental run. A production implementation should support rejected-record reprocessing or an appropriate checkpoint recovery strategy.

## 14. Future Enhancements

- Add automatic retry with exponential backoff.
- Implement configurable API rate limiting.
- Add a dedicated quarantine reprocessing process.
- Improve checkpoint recovery and transactional consistency.
- Add structured JSON logging.
- Add monitoring and alerting.
- Introduce Docker-based deployment.
- Add cloud database and cloud storage support.
- Implement orchestration using Apache Airflow.

## 15. Conclusion

This project demonstrates an end-to-end API data ingestion workflow using Python, FastAPI, and SQL Server.

It focuses on reliable extraction, data quality, incremental processing, duplicate prevention, failure handling, and monitoring.

The project can be extended into a production-grade data engineering pipeline with improved orchestration, monitoring, retry mechanisms, and cloud integration.