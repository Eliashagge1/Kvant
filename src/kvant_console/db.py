from contextlib import contextmanager
from pathlib import Path
import duckdb
SCHEMA="""
CREATE TABLE IF NOT EXISTS raw_bars(asset_id VARCHAR,session_date DATE,open DOUBLE,high DOUBLE,low DOUBLE,close DOUBLE,volume DOUBLE,provider VARCHAR,retrieved_at TIMESTAMPTZ,payload_hash VARCHAR,vendor_adjusted_close DOUBLE,canonical BOOLEAN,PRIMARY KEY(asset_id,session_date,provider));
CREATE TABLE IF NOT EXISTS corporate_actions(event_id VARCHAR PRIMARY KEY,asset_id VARCHAR,event_type VARCHAR,ex_date DATE,available_at TIMESTAMPTZ,provider VARCHAR,payload_hash VARCHAR,cash_amount DOUBLE,currency VARCHAR,split_coefficient DOUBLE,review_status VARCHAR DEFAULT 'accepted');
CREATE TABLE IF NOT EXISTS adjusted_series(asset_id VARCHAR,session_date DATE,split_adjusted_close DOUBLE,total_return_index DOUBLE,build_hash VARCHAR,PRIMARY KEY(asset_id,session_date));
CREATE TABLE IF NOT EXISTS batches(batch_id VARCHAR PRIMARY KEY,kind VARCHAR,started_at TIMESTAMPTZ,committed_at TIMESTAMPTZ,status VARCHAR,required_assets INTEGER,received_assets INTEGER,details JSON);
CREATE TABLE IF NOT EXISTS admission(asset_id VARCHAR PRIMARY KEY,status VARCHAR,validated_at TIMESTAMPTZ,critical_count INTEGER,warning_count INTEGER,report JSON);
CREATE TABLE IF NOT EXISTS experiments(run_id VARCHAR PRIMARY KEY,created_at TIMESTAMPTZ,git_commit VARCHAR,data_hash VARCHAR,feature_hash VARCHAR,model_hash VARCHAR,parameters JSON,metrics JSON,tested_variants INTEGER);
CREATE TABLE IF NOT EXISTS model_results(run_id VARCHAR,model VARCHAR,mse DOUBLE,ic DOUBLE,sharpe DOUBLE,is_selected BOOLEAN);
CREATE TABLE IF NOT EXISTS backtest_daily(run_id VARCHAR,session_date DATE,equity DOUBLE,benchmark DOUBLE,daily_return DOUBLE,cost DOUBLE);
CREATE TABLE IF NOT EXISTS paper_cash(currency VARCHAR PRIMARY KEY,amount DOUBLE);
CREATE TABLE IF NOT EXISTS paper_positions(asset_id VARCHAR PRIMARY KEY,quantity DOUBLE,average_price DOUBLE,last_price DOUBLE,updated_at TIMESTAMPTZ);
CREATE TABLE IF NOT EXISTS paper_fills(fill_id VARCHAR PRIMARY KEY,session_date DATE,asset_id VARCHAR,quantity DOUBLE,price DOUBLE,commission DOUBLE,impact DOUBLE);
CREATE TABLE IF NOT EXISTS review_queue(review_id VARCHAR PRIMARY KEY,created_at TIMESTAMPTZ,type VARCHAR,asset_id VARCHAR,severity VARCHAR,reason VARCHAR,raw_payload JSON,status VARCHAR,resolved_at TIMESTAMPTZ,resolution VARCHAR);
CREATE TABLE IF NOT EXISTS reconciliation(run_id VARCHAR,row_number INTEGER,status VARCHAR,kind VARCHAR,asset VARCHAR,amount DOUBLE,currency VARCHAR,details JSON);
CREATE TABLE IF NOT EXISTS call_ledger(call_date DATE,endpoint VARCHAR,symbol VARCHAR,status VARCHAR,created_at TIMESTAMPTZ);
"""
class DB:
    def __init__(self,path:Path): self.path=path;path.parent.mkdir(parents=True,exist_ok=True);self.c=duckdb.connect(str(path));self.c.execute(SCHEMA)
    def close(self): self.c.close()
    @contextmanager
    def tx(self):
        self.c.execute("BEGIN")
        try: yield; self.c.execute("COMMIT")
        except Exception: self.c.execute("ROLLBACK"); raise
