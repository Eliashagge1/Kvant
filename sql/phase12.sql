-- Append-only audit tables. Application roles receive INSERT/SELECT only.
CREATE TABLE IF NOT EXISTS experiment_runs(
 run_id UUID PRIMARY KEY, experiment_name VARCHAR NOT NULL, started_at TIMESTAMP NOT NULL,
 completed_at TIMESTAMP, git_commit VARCHAR NOT NULL, code_version VARCHAR,
 data_snapshot VARCHAR NOT NULL, feature_spec_hash VARCHAR NOT NULL,
 model_artifact_hash VARCHAR, tested_variants UINTEGER NOT NULL,
 parameters JSON NOT NULL, metrics JSON NOT NULL, created_at TIMESTAMP DEFAULT current_timestamp
);
CREATE TABLE IF NOT EXISTS monitoring_metrics(
 metric_id UUID PRIMARY KEY, calculated_at TIMESTAMP NOT NULL, model_version VARCHAR NOT NULL,
 symbol VARCHAR, window_start TIMESTAMP, window_end TIMESTAMP, metric_name VARCHAR NOT NULL,
 metric_value DOUBLE NOT NULL, observation_count UINTEGER NOT NULL, metadata JSON,
 created_at TIMESTAMP DEFAULT current_timestamp
);
CREATE TABLE IF NOT EXISTS provider_ingestion_audit(
 ingestion_id UUID PRIMARY KEY, provider VARCHAR NOT NULL, dataset VARCHAR NOT NULL,
 source_file VARCHAR NOT NULL, source_sha256 VARCHAR NOT NULL, imported_at TIMESTAMP NOT NULL,
 minimum_date DATE, maximum_date DATE, row_count UBIGINT NOT NULL, rejected_rows UBIGINT NOT NULL,
 metadata JSON
);

-- Never update or delete experiment history. Use a correction row referencing the original run.
CREATE TABLE IF NOT EXISTS experiment_corrections(
 correction_id UUID PRIMARY KEY, original_run_id UUID NOT NULL, corrected_at TIMESTAMP NOT NULL,
 reason VARCHAR NOT NULL, replacement_run_id UUID
);

-- Structural point-in-time view. available_date, never period_end_date, controls visibility.
-- safety_lag_days must be injected as a validated nonnegative integer by the data layer.
CREATE OR REPLACE MACRO point_in_time_fundamentals(safety_lag_days) AS TABLE
SELECT p.ticker,p.date,f.period_end_date,f.available_date,f.field,f.value
FROM prices p
ASOF LEFT JOIN fundamentals f
 ON p.ticker=f.ticker
AND p.date >= f.available_date + safety_lag_days * INTERVAL 1 DAY;

CREATE OR REPLACE VIEW valid_universe_membership AS
SELECT ticker,start_date,end_date
FROM universe_membership
WHERE end_date IS NULL OR end_date>=start_date;
