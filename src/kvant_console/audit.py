import hashlib,json,subprocess,zipfile,uuid
from datetime import datetime,timezone
from pathlib import Path
def git():
    try:return subprocess.check_output(["git","rev-parse","HEAD"],text=True,stderr=subprocess.DEVNULL).strip()
    except Exception:return "unavailable"
def export(db,config,path:Path):
    payload={"schema_version":1,"generated_at":datetime.now(timezone.utc).isoformat(),"git_commit":git(),"config":config.model_dump(),"latest_batch":db.c.execute("SELECT * FROM batches ORDER BY started_at DESC LIMIT 1").fetchone(),"admission":db.c.execute("SELECT * FROM admission").fetchall(),"experiments":db.c.execute("SELECT * FROM experiments ORDER BY created_at DESC").fetchall(),"model_results":db.c.execute("SELECT * FROM model_results").fetchall(),"paper":db.c.execute("SELECT * FROM paper_positions").fetchall(),"open_reviews":db.c.execute("SELECT * FROM review_queue WHERE status='open'").fetchall()}
    data=json.dumps(payload,default=str,indent=2).encode()
    digest=hashlib.sha256(data).hexdigest()
    path.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("audit.json",data)
        z.writestr("sha256.txt",digest+"  audit.json\n")
    return {"path":str(path),"sha256":digest}
