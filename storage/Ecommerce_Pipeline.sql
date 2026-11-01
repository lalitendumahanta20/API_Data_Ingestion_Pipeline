create database ecommerce_pipeline;
go

use ecommerce_pipeline;
go

SELECT DB_NAME() AS database_name;

-- 1. Track Every Pipeline Execution
create table pipeline_runs(
	run_id uniqueidentifier primary key,
	start_time datetime2 not null default sysutcdatetime(),
	end_time datetime2 null,

	status varchar(100) not null
		check (status in ('RUNNING','SUCCESS','FAILED')),

	records_fetched int not null default 0,
	records_inserted int not null default 0,
	records_updated int not null default 0,
	records_rejected int not null default 0,

	error_message nvarchar(max) null
);
go


--2. Store Original API Response
create table raw_api_responses(
	response_id bigint identity(1,1) primary key,
	run_id uniqueidentifier not null,

	endpoint nvarchar(100) not null,
	page_number int not null,
	http_status int not null,

	request_params nvarchar(max) null,
	response_json nvarchar(max) not null,

	fetched_at datetime2 not null default sysutcdatetime(),

	constraint FK_raw_pipeline_run
		foreign key(run_id)
		references pipeline_runs(run_id),

	constraint CK_raw_page
		check (page_number >=1),

	constraint CK_raw_json
		check (isjson(response_json)=1),

	constraint UQ_raw_run_endpiont_page
		unique (run_id,endpoint,page_number)
);
go

-- 3. Store Valid Customer
create table customers(
	customer_id int primary key,
	customer_name nvarchar(150) not null,
	email nvarchar(255) not null,

	source_created_at datetimeoffset not null,
	source_updated_at datetimeoffset not null,

	inserted_at datetime2 not null default sysutcdatetime(),
	modified_at datetime2 not null default sysutcdatetime()
);
go

-- 4. Store Valid Orders
create table orders(
	order_id int primary key,
	customer_id int not null,

	order_amount decimal(18,2) not null,
	order_status varchar(30) not null,

	source_created_at datetimeoffset not null,
	source_updated_at datetimeoffset not null,

	inserted_at datetime2 not null default sysutcdatetime(),
	modified_at datetime2 not null default sysutcdatetime(),

	constraint FK_orders_customers
		foreign key (customer_id)
		references customers(customer_id),

	constraint CK_order_status
		check (order_status in ('COMPLETED','PENDING','CANCELLED'))
);
go

--5. Store Invalid Records for Investigation
create table rejected_records(
	rejected_id bigint identity(1,1) primary key,

	run_id uniqueidentifier not null,
	response_id bigint null,

	entity_type varchar(30) not null,
	original_record_json nvarchar(max) not null,
	error_reason nvarchar(max) not null,

	rejected_at datetime2 not null default sysutcdatetime(),

	constraint FK_rejected_pipeline_run
		foreign key (run_id)
		references pipeline_runs(run_id),

	constraint FK_rejected_raw_response
		foreign key (response_id)
		references raw_api_responses(response_id),

	constraint CK_rejected_json
		check (isjson(original_record_json)=1)
);
go

-- 6. Remember the last successful ingestion position
create table checkpoints(
	entity_name varchar(50) primary key,

	last_successful_updated_at datetimeoffset null,
	last_run_id uniqueidentifier null,

	updated_at datetime2 not null default sysutcdatetime(),

	constraint FK_checkpoint_pipeline_run
		foreign key (last_run_id)
		references pipeline_runs(run_id)
);
go

-- Helpful indexes for common query
create index IX_orders_customer_id
on orders(customer_id);
go

create index IX_orders_source_updated_at
on orders(source_updated_at);
go

create index IX_raw_fetched_at
on raw_api_responses(fetched_at);
go

PRINT 'All six pipeline tables created successfully!';
GO

select table_schema,table_name
from INFORMATION_SCHEMA.TABLES
where TABLE_TYPE='BASE TABLE'
order by TABLE_NAME

exec sp_help 'dbo.customers';
exec sp_help 'dbo.orders';

select * from pipeline_runs
order by start_time desc;

select * from customers;

select * from orders;

select * from raw_api_responses;

select
    run_id,
    status,
    records_fetched,
    records_inserted,
	records_rejected,
    error_message
from dbo.pipeline_runs
order by start_time desc;

select
    endpoint,
    page_number,
    http_status,
    fetched_at
from dbo.raw_api_responses
order by response_id desc;

select COUNT(*) AS total_customers
from dbo.customers;

select COUNT(*) AS total_orders
from dbo.orders;

select
    rejected_id,
    entity_type,
    original_record_json,
    error_reason,
    rejected_at
from rejected_records
order by rejected_id DESC;

select * from checkpoints;

select top 10
    run_id,
    start_time,
    end_time,
    status,
    records_fetched,
    records_inserted,
    records_updated,
    records_rejected,
    error_message
from dbo.pipeline_runs
order by start_time desc;