from fastapi import FastAPI,HTTPException,UploadFile,File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import json,uuid,uvicorn
from . import settings
from .config import Universe,load,save
from .db import DB
from .secrets import set_alpha_key,status as key_status
from .alpha import Client
from .data import alpha_update,yahoo_bootstrap,overlap_admission
from .modeling import run_baselines,run_backtest
from .paper import Paper
from .avanza import reconcile
from .audit import export
settings.ensure_dirs();app=FastAPI(title="Kvant Local API",version="0.2.0");app.add_middleware(CORSMiddleware,allow_origins=["http://127.0.0.1:5173","http://localhost:5173"],allow_credentials=False,allow_methods=["*"] ,allow_headers=["*"])
def db():return DB(settings.DB)
def universe():return load(settings.CONFIG)
class KeyIn(BaseModel):api_key:str
@app.get("/api/status")
def get_status():
 d=db();latest=d.c.execute("SELECT batch_id,status,committed_at,required_assets,received_assets FROM batches ORDER BY started_at DESC LIMIT 1").fetchone();calls=d.c.execute("SELECT count(*) FROM call_ledger WHERE call_date=current_date").fetchone()[0];open_reviews=d.c.execute("SELECT count(*) FROM review_queue WHERE status='open'").fetchone()[0];d.close();return {"key":key_status(),"latest_batch":latest,"calls_today":calls,"open_reviews":open_reviews}
@app.post("/api/config/key")
def key(x:KeyIn):set_alpha_key(x.api_key);return {"configured":True}
@app.get("/api/universe",response_model=Universe)
def get_universe():return universe()
@app.put("/api/universe",response_model=Universe)
def put_universe(x:Universe):save(settings.CONFIG,x);return x
@app.get("/api/symbols/search")
def symbols(q:str):return Client().search(q)
@app.post("/api/data/bootstrap/alpha")
def bootstrap_alpha():
 d=db()
 try:return {"batch_id":alpha_update(d,universe(),True)}
 finally:d.close()
@app.post("/api/data/bootstrap/yahoo")
def bootstrap_yahoo():return yahoo_bootstrap(universe(),settings.RESEARCH)
@app.post("/api/data/update")
def update():
 d=db()
 try:return {"batch_id":alpha_update(d,universe(),False)}
 finally:d.close()
@app.post("/api/data/validate-overlap")
def overlap():
 d=db()
 try:return overlap_admission(d,universe(),settings.RESEARCH)
 finally:d.close()
@app.get("/api/data/freshness")
def freshness():
 d=db();rows=d.c.execute("SELECT asset_id,max(session_date) last_date,count(*) rows FROM raw_bars WHERE canonical=true GROUP BY asset_id ORDER BY asset_id").fetchall();ad={x[0]:x[1] for x in d.c.execute("SELECT asset_id,status FROM admission").fetchall()};d.close();return [{"asset_id":a,"last_date":str(dt),"rows":n,"admission":ad.get(a,"unvalidated")} for a,dt,n in rows]
@app.get("/api/data/adjustments/{asset_id}")
def adjustments(asset_id:str):
 d=db();rows=d.c.execute("SELECT session_date,split_adjusted_close,total_return_index FROM adjusted_series WHERE asset_id=? ORDER BY session_date",[asset_id]).fetchall();d.close();return [{"date":str(x[0]),"adjusted":x[1],"total_return":x[2]} for x in rows]
@app.post("/api/models/baseline")
def models():
 d=db()
 try:return run_baselines(d)
 finally:d.close()
@app.get("/api/models/results")
def model_results():
 d=db();rows=d.c.execute("SELECT run_id,model,mse,ic,sharpe,is_selected FROM model_results ORDER BY rowid DESC").fetchall();d.close();return [{"run_id":r,"model":m,"mse":e,"ic":i,"sharpe":s,"selected":z} for r,m,e,i,s,z in rows]
@app.post("/api/backtests")
def backtest():
 d=db()
 try:return run_backtest(d)
 finally:d.close()
@app.get("/api/backtests/latest")
def backtest_latest():
 d=db();run=d.c.execute("SELECT run_id FROM backtest_daily ORDER BY rowid DESC LIMIT 1").fetchone();rows=[] if not run else d.c.execute("SELECT session_date,equity,benchmark,daily_return,cost FROM backtest_daily WHERE run_id=? ORDER BY session_date",[run[0]]).fetchall();d.close();return [{"date":str(a),"equity":b,"benchmark":c,"return":e,"cost":f} for a,b,c,e,f in rows]
@app.get("/api/paper/portfolio")
def paper():
 d=db();p=Paper(d);p.mark_from_canonical();x=p.snapshot();d.close();return x
@app.post("/api/reconciliation/avanza")
async def avanza(file:UploadFile=File(...)):
 d=db()
 try:return reconcile(d,await file.read())
 finally:d.close()
@app.get("/api/reviews")
def reviews():
 d=db();rows=d.c.execute("SELECT review_id,created_at,type,asset_id,severity,reason,status FROM review_queue ORDER BY created_at DESC").fetchall();d.close();return [{"id":a,"created_at":str(b),"type":c,"asset_id":e,"severity":f,"reason":g,"status":h} for a,b,c,e,f,g,h in rows]
@app.post("/api/reviews/{review_id}/resolve")
def resolve(review_id:str,resolution:str="reviewed"):
 d=db();d.c.execute("UPDATE review_queue SET status='resolved',resolved_at=current_timestamp,resolution=? WHERE review_id=? AND status='open'",[resolution,review_id]);d.close();return {"resolved":True}
@app.post("/api/audit/export")
def audit():
 d=db();path=settings.ARTIFACTS/f"audit-{uuid.uuid4()}.zip";result=export(d,universe(),path);d.close();return result
@app.get("/api/audit/download")
def download(path:str):
 p=Path(path).resolve();root=settings.ARTIFACTS.resolve()
 if root not in p.parents:raise HTTPException(403,"invalid audit path")
 return FileResponse(p,filename=p.name)
def main():uvicorn.run(app,host="127.0.0.1",port=8765)
