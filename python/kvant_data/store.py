import json
from contextlib import contextmanager
from decimal import Decimal
import duckdb
SCHEMA="""CREATE TABLE IF NOT EXISTS raw_bars(asset_id VARCHAR,session_date DATE,open DECIMAL(28,8),high DECIMAL(28,8),low DECIMAL(28,8),close DECIMAL(28,8),volume DECIMAL(28,6),provider VARCHAR,retrieved_at TIMESTAMPTZ,payload_hash VARCHAR,vendor_adjusted_close DECIMAL(28,8),canonical BOOLEAN,PRIMARY KEY(asset_id,session_date,provider));
CREATE TABLE IF NOT EXISTS corporate_actions(event_id VARCHAR PRIMARY KEY,asset_id VARCHAR,event_type VARCHAR,ex_date DATE,available_at TIMESTAMPTZ,provider VARCHAR,payload_hash VARCHAR,cash_amount DECIMAL(28,8),currency VARCHAR,split_coefficient DECIMAL(28,8),review_status VARCHAR DEFAULT 'accepted');
CREATE TABLE IF NOT EXISTS adjusted_series(asset_id VARCHAR,session_date DATE,split_adjusted_close DECIMAL(28,8),total_return_index DECIMAL(38,12),build_hash VARCHAR,PRIMARY KEY(asset_id,session_date));
CREATE TABLE IF NOT EXISTS data_batches(batch_id VARCHAR PRIMARY KEY,started_at TIMESTAMPTZ,committed_at TIMESTAMPTZ,status VARCHAR,required_assets UINTEGER,received_assets UINTEGER,details JSON);
CREATE TABLE IF NOT EXISTS data_revisions(asset_id VARCHAR,session_date DATE,field VARCHAR,old_value VARCHAR,new_value VARCHAR,provider VARCHAR,detected_at TIMESTAMPTZ DEFAULT current_timestamp);
CREATE TABLE IF NOT EXISTS asset_admission(asset_id VARCHAR PRIMARY KEY,admitted BOOLEAN,validated_at TIMESTAMPTZ,reason VARCHAR);"""
class Store:
 def __init__(self,path):self.db=duckdb.connect(str(path));self.db.execute(SCHEMA)
 @contextmanager
 def tx(self):
  self.db.execute('BEGIN')
  try:yield;self.db.execute('COMMIT')
  except Exception:self.db.execute('ROLLBACK');raise
 def commit_batch(self,batch,required,results):
  missing=set(required)-set(results)
  if missing:raise RuntimeError(f'incomplete universe: {sorted(missing)}')
  with self.tx():
   self.db.execute("INSERT INTO data_batches VALUES (?,current_timestamp,NULL,'staging',?,?,?)",[batch,len(required),len(results),json.dumps({'assets':sorted(results)})])
   for _,(bars,actions) in results.items():
    for b in bars:
     old=self.db.execute('SELECT open,high,low,close,volume FROM raw_bars WHERE asset_id=? AND session_date=? AND provider=?',[b.asset_id,b.session_date,b.provider]).fetchone()
     values=[b.open,b.high,b.low,b.close,b.volume]
     if old:
      for field,o,n in zip(('open','high','low','close','volume'),old,values):
       if Decimal(str(o))!=n:self.db.execute('INSERT INTO data_revisions(asset_id,session_date,field,old_value,new_value,provider) VALUES (?,?,?,?,?,?)',[b.asset_id,b.session_date,field,str(o),str(n),b.provider])
     self.db.execute('INSERT OR REPLACE INTO raw_bars VALUES (?,?,?,?,?,?,?,?,?,?,?,true)',[b.asset_id,b.session_date,b.open,b.high,b.low,b.close,b.volume,b.provider,b.retrieved_at,b.payload_hash,b.vendor_adjusted_close])
    for a in actions:self.db.execute('INSERT OR REPLACE INTO corporate_actions(event_id,asset_id,event_type,ex_date,available_at,provider,payload_hash,cash_amount,currency,split_coefficient) VALUES (?,?,?,?,?,?,?,?,?,?)',[a.event_id,a.asset_id,a.event_type,a.ex_date,a.available_at,a.provider,a.payload_hash,a.cash_amount,a.currency,a.split_coefficient])
   self.db.execute("UPDATE data_batches SET committed_at=current_timestamp,status='committed' WHERE batch_id=?",[batch])
