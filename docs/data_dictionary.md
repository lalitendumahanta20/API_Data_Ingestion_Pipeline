# Data Dictionary – E-Commerce API Ingestion Pipeline

## 1. Overview

This document describes the main entities, fields, data types, relationships, and validation rules used in the e-commerce ingestion pipeline.

## 2. Customers Entity

| Field | Data Type | Description | Validation |
|---|---|---|---|
| customer_id | Integer | Unique customer identifier | Required, unique, positive |
| customer_name | String | Customer's name | Required, non-empty |
| email | String | Customer email address | Valid email format |
| created_at | Timestamp | Customer creation time | Valid timestamp |
| updated_at | Timestamp | Last update time | Valid timestamp |

**Primary Key:** customer_id

## 3. Orders Entity

| Field | Data Type | Description | Validation |
|---|---|---|---|
| order_id | Integer | Unique order identifier | Required, unique, positive |
| customer_id | Integer | Customer associated with the order | Must reference an existing customer |
| amount | Decimal | Order amount | Required, positive |
| status | String | Order status | Must be an accepted business status |
| created_at | Timestamp | Order creation time | Valid timestamp |
| updated_at | Timestamp | Last update time | Valid timestamp |

**Primary Key:** order_id

**Foreign Key:** customer_id references customers.customer_id.

## 4. Pipeline Metadata

### pipeline_runs
Tracks each ingestion execution.

Important fields:
- run_id: Unique execution identifier.
- start_time: Pipeline start timestamp.
- end_time: Pipeline completion timestamp.
- status: SUCCESS or FAILED.
- fetched_count: Records fetched from the API.
- inserted_count: New records inserted.
- updated_count: Existing records updated.
- rejected_count: Invalid records rejected.
- error_message: Failure details.

### rejected_records
Stores invalid records for investigation.

Important fields:
- run_id: Related pipeline execution.
- entity_type: Customer or order.
- original_record_json: Original rejected record.
- error_reason: Reason for rejection.

### checkpoints
Stores the last successful incremental ingestion timestamp.

## 5. Relationships

- One customer can have multiple orders.
- Each order belongs to one customer.
- Every pipeline run can produce multiple rejected records.
- Checkpoints track incremental ingestion progress.

## 6. Data Quality Rules

1. Primary keys must be unique and non-null.
2. Customer IDs must be positive integers.
3. Email addresses must follow a valid format.
4. Order amounts must be positive.
5. Every order must reference an existing customer.
6. Timestamps must be valid and consistently formatted.
7. Invalid records must be quarantined instead of silently discarded.

## 7. Assumptions

- Customer and order IDs are supplied by the source API.
- API timestamps are interpreted as UTC.
- The latest valid customer/order state is maintained in the target tables.
- Invalid records are stored separately for investigation.
- Incremental processing uses a checkpoint timestamp.