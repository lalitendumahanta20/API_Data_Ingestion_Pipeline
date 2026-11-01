use ecommerce_pipeline;
go

-- Create the run reconciliation report
select run_id,status,records_fetched,records_inserted,records_updated,records_rejected,
		records_fetched
			- records_inserted
			- records_updated
			- records_rejected as records_unchanged,
		case
			when records_fetched=
				records_inserted
				+ records_updated
				+ records_rejected
				+ (
					records_fetched
					- records_inserted
					- records_updated
					- records_rejected
				   )
			then 'RECONCILED'
			else 'MISMATCH'
		end as reconciliation_status
from pipeline_runs
order by start_time desc;

-- Create the data quality report
select
    entity_type,
    error_reason,
    COUNT(*) as rejected_count
from dbo.rejected_records
group by entity_type,error_reason
order by rejected_count desc;

-- Create a rejection percentage report
select
    run_id,
    records_fetched,
    records_rejected,

    records_fetched - records_rejected
        as valid_records,

    cast(
        records_rejected * 100.0
        / NULLIF(records_fetched, 0)
        as DECIMAL(5,2)
    ) as rejection_percentage,

    cast(
        (records_fetched - records_rejected) * 100.0
        / NULLIF(records_fetched, 0)
        as DECIMAL(5,2)
    ) as valid_percentage

from dbo.pipeline_runs
order by start_time desc;

-- Compare pipeline rejection counts with actual rejected records
WITH RejectionSummary as
(
    select
        run_id,
        COUNT(*) AS actual_rejected_records
    from dbo.rejected_records
    group by run_id
)

select
    p.run_id,
    p.records_rejected as pipeline_rejected_count,

    ISNULL(r.actual_rejected_records, 0)
        as database_rejected_count,

    p.records_rejected
        - ISNULL(r.actual_rejected_records, 0)
        as count_difference,

    case
        when p.records_rejected =
             ISNULL(r.actual_rejected_records, 0)
        then 'MATCH'
        else 'MISMATCH'
    end as rejection_check

from dbo.pipeline_runs p
left join RejectionSummary r on p.run_id = r.run_id
order by p.start_time desc;

-- Create a database summary report
select
    'Customers' AS entity_name,
    COUNT(*) AS total_records
from dbo.customers
union all
select
    'Orders' AS entity_name,
    COUNT(*) AS total_records
from dbo.orders;

-- Create a pipeline run history report
select run_id,start_time,end_time,status,records_fetched,records_inserted,records_updated,records_rejected,
    DATEDIFF(
        SECOND,
        start_time,
        end_time
    ) as execution_time_seconds

from dbo.pipeline_runs
order by start_time desc;

--verification
select p.run_id,p.records_fetched,p.records_inserted,p.records_updated,p.records_rejected,
    COUNT(r.rejected_id) as actual_rejected_records,
    case
        when p.records_rejected = COUNT(r.rejected_id)
        then 'MATCH'
        else 'MISMATCH'
    end as reconciliation_status
from dbo.pipeline_runs p
left join dbo.rejected_records r
    on p.run_id = r.run_id
where p.run_id = '49913510-D84C-4BDC-96BA-B171B3D0BB9D'
group by p.run_id,p.records_fetched,p.records_inserted,p.records_updated,p.records_rejected;