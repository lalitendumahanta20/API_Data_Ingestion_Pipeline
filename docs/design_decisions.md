# Design Decisions and Trade-offs

## 1. Architecture

The pipeline follows a modular ingestion architecture:

1. FastAPI provides mock e-commerce API endpoints.
2. API client fetches paginated data.
3. Retry and rate-limiting mechanisms handle temporary API failures.
4. Validation checks data quality and business rules.
5. Invalid records are moved to a rejection table.
6. Valid records are inserted or updated in SQL Server.
7. Pipeline execution metrics and logs support monitoring.

## 2. Technology Choices

| Technology | Reason |
|---|---|
| Python | Simple and flexible for data engineering |
| FastAPI | Lightweight mock API service |
| Requests | HTTP communication with retry handling |
| SQL Server | Relational storage and data integrity |
| PyODBC | SQL Server connectivity |
| Pandas | Useful for data analysis and reconciliation |
| Pytest | Automated testing |

## 3. Key Design Decisions

### Pagination
Data is fetched in pages to avoid retrieving the entire dataset in one API request.

**Trade-off:** More API calls are required, but memory consumption is controlled.

### Retry Mechanism
Temporary errors such as HTTP 500, 502, 503, 504 and 429 are retried.

**Trade-off:** Retries improve reliability but can increase execution time.

### Rate Limiting
Requests are restricted according to the configured requests-per-second value.

**Trade-off:** This protects the source API but reduces maximum ingestion speed.

### Incremental Ingestion
A checkpoint timestamp is used to fetch records updated since the previous successful run.

**Trade-off:** Less data is processed during normal runs, but late-arriving and out-of-order records require careful handling.

### Validation and Quarantine
Invalid records are stored in a rejection table with their original payload and rejection reason.

**Trade-off:** The pipeline can continue processing valid records, but rejected records need a reprocessing strategy.

### Idempotent Upsert
Existing records are updated only when the incoming source timestamp is newer. Repeated unchanged records should not create duplicate rows.

**Trade-off:** This simplifies safe reruns but requires reliable source keys and timestamps.

### SQL Server
A relational database stores customers, orders, pipeline metadata, and rejected records.

**Trade-off:** Strong relational integrity is useful, but database connectivity and configuration require additional setup.

## 4. Failure Handling

- API errors are retried where appropriate.
- Database failures are logged.
- Pipeline execution status is recorded.
- Invalid records are quarantined.
- Repeated ingestion should not create duplicate business records.

## 5. Known Limitations

- The mock API does not represent every real-world API behavior.
- Small performance tests do not establish production-scale throughput.
- The target customer and order tables maintain the latest state rather than a complete historical change log.
- Large-scale ingestion needs additional performance and recovery testing.
- Checkpoint handling should be tested with late-arriving and previously rejected records.

## 6. Future Improvements

- Add automated quarantine reprocessing.
- Add checkpoint overlap or replay handling for late-arriving records.
- Add schema-version detection.
- Add historical tracking for customer and order changes.
- Add batch-size and database-write performance optimization.
- Add CI/CD with automated tests.