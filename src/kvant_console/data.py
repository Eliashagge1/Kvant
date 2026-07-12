from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,uuid
import pandas as pd
import yfinance as yf
from .alpha import Client

def commit_batch(db,kind,universe,results,errors):
    required=[a.asset_id for a in universe.assets if a.required];missing=set(required)-set(results);batch=f"{kind}-{uuid.uuid4()}"
    if missing:
        db.c.execute("INSERT INTO batches VALUES (?,?,current_timestamp,current_timestamp,'rejected',?,?,?)",[batch,kind,len(required),len(results),json.dumps({"errors":errors,"missing":sorted(missing)})]);raise RuntimeError(f"fail-closed: missing {sorted(missing)}")
    with db.tx():
        db.c.execute("INSERT INTO batches VALUES (?,?,current_timestamp,NULL,'staging',?,?,?)",[batch,kind,len(required),len(results),json.dumps({"assets":sorted(results)})])
        for asset,(bars,actions) in results.items():
            for b in bars: db.c.execute("INSERT OR REPLACE INTO raw_bars VALUES (?,?,?,?,?,?,?,?,?,?,?,true)",[asset,b["date"],b["open"],b["high"],b["low"],b["close"],b["volume"],"alpha_vantage",b["retrieved_at"],b["hash"],b["adjusted"]])
            for a in actions: db.c.execute("INSERT OR REPLACE INTO corporate_actions(event_id,asset_id,event_type,ex_date,available_at,provider,payload_hash,cash_amount,currency,split_coefficient) VALUES (?,?,?,?,?,?,?,?,?,?)",a)
        db.c.execute("UPDATE batches SET committed_at=current_timestamp,status='committed' WHERE batch_id=?",[batch])
    return batch

def alpha_update(db,universe,full=False,client=None):
    client=client or Client();results={};errors={}
    for a in universe.assets:
        try: results[a.asset_id]=client.daily(a,full);db.c.execute("INSERT INTO call_ledger VALUES (current_date,'TIME_SERIES_DAILY_ADJUSTED',?,'ok',current_timestamp)",[a.alpha_symbol])
        except Exception as e: errors[a.asset_id]=str(e);db.c.execute("INSERT INTO call_ledger VALUES (current_date,'TIME_SERIES_DAILY_ADJUSTED',?,'failed',current_timestamp)",[a.alpha_symbol])
    batch=commit_batch(db,"bootstrap" if full else "daily",universe,results,errors)
    for a in universe.assets: rebuild_adjustments(db,a.asset_id)
    return batch

def yahoo_bootstrap(universe,target:Path):
    target.mkdir(parents=True,exist_ok=True);manifest={"provider":"yfinance","canonical":False,"eligible_for_live_inference":False,"assets":[]}
    for a in universe.assets:
        df=yf.download(a.yahoo_symbol,period="max",auto_adjust=False,actions=True,progress=False,threads=False,multi_level_index=False)
        if df.empty: raise RuntimeError(f"no Yahoo data: {a.yahoo_symbol}")
        df=df.reset_index();df.columns=[str(c).lower().replace(" ","_") for c in df.columns];df["asset_id"]=a.asset_id;df["canonical"]=False
        p=target/f"{a.asset_id.replace(':','_')}.parquet";df.to_parquet(p,index=False);manifest["assets"].append({"asset_id":a.asset_id,"file":p.name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
    (target/"manifest.json").write_text(json.dumps(manifest,indent=2));return manifest

def rebuild_adjustments(db,asset):
    bars=db.c.execute("SELECT session_date,close FROM raw_bars WHERE asset_id=? AND canonical=true ORDER BY session_date",[asset]).fetchall();acts=db.c.execute("SELECT ex_date,event_type,coalesce(cash_amount,0),coalesce(split_coefficient,1),event_id FROM corporate_actions WHERE asset_id=? AND review_status='accepted' ORDER BY ex_date",[asset]).fetchall();by={};ids=[]
    for d,t,c,s,e in acts: by.setdefault(d,[]).append((t,float(c),float(s)));ids.append(e)
    factor=1.;rows=[]
    for d,close in reversed(bars):
        rows.append([d,float(close)/factor,None])
        for t,_,s in by.get(d,[]):
            if t=="split":factor*=s
    rows.reverse();tri=1.;prev=None
    for r in rows:
        d,adj,_=r;div=sum(c for t,c,_ in by.get(d,[]) if t=="cash_dividend")
        if prev is not None:tri*=((adj+div)/prev)
        r[2]=tri;prev=adj
    h=hashlib.sha256((asset+"|".join(ids)).encode()).hexdigest()
    with db.tx(): db.c.execute("DELETE FROM adjusted_series WHERE asset_id=?",[asset]);db.c.executemany("INSERT INTO adjusted_series VALUES (?,?,?,?,?)",[[asset,d,a,t,h] for d,a,t in rows])

def overlap_admission(db,universe,research:Path):
    reports=[]
    for a in universe.assets:
        ap=db.c.execute("SELECT session_date,open,high,low,close,volume FROM raw_bars WHERE asset_id=? AND provider='alpha_vantage' ORDER BY session_date",[a.asset_id]).df();p=research/f"{a.asset_id.replace(':','_')}.parquet"
        critical=[];warnings=[]
        if not p.exists():critical.append("YAHOO_RESEARCH_FILE_MISSING")
        else:
            yp=pd.read_parquet(p);yp["date"]=pd.to_datetime(yp["date"]).dt.date;merged=ap.merge(yp,left_on="session_date",right_on="date",suffixes=("_a","_y")).tail(universe.overlap_sessions)
            if len(merged)<min(20,universe.overlap_sessions):critical.append("MISSING_OVERLAP")
            for field in ("open","high","low","close"):
                bad=((merged[f"{field}_a"]-merged[f"{field}_y"]).abs()/merged[[f"{field}_a",f"{field}_y"]].abs().max(axis=1).clip(lower=1)>.0001).sum()
                if bad:critical.append(f"{field.upper()}_MISMATCH:{bad}")
            vb=((merged.volume_a-merged.volume_y).abs()/merged[["volume_a","volume_y"]].abs().max(axis=1).clip(lower=1)>.02).sum()
            if vb:warnings.append(f"VOLUME_CONVENTION:{vb}")
        status="admitted" if not critical else "quarantined";report={"asset_id":a.asset_id,"status":status,"critical":critical,"warnings":warnings}
        db.c.execute("INSERT OR REPLACE INTO admission VALUES (?, ?, current_timestamp, ?, ?, ?)",[a.asset_id,status,len(critical),len(warnings),json.dumps(report)]);reports.append(report)
    return reports
