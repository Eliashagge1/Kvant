import json,os,tempfile
from pathlib import Path
from datetime import datetime,timezone
from fastapi.testclient import TestClient
class FakeKeyring:
 value=None
 def set_password(self,*a):self.value=a[-1]
 def get_password(self,*a):return self.value

def test_full_vertical(monkeypatch):
 with tempfile.TemporaryDirectory() as td:
  home=Path(td);monkeypatch.setenv("KVANT_HOME",str(home));monkeypatch.setenv("KVANT_DB",str(home/"k.duckdb"));monkeypatch.setenv("KVANT_CONFIG",str(home/"u.json"));monkeypatch.setenv("KVANT_RESEARCH",str(home/"research"));monkeypatch.setenv("KVANT_ARTIFACTS",str(home/"artifacts"))
  import importlib
  import kvant_console.settings as settings;importlib.reload(settings)
  settings.ensure_dirs();settings.CONFIG.write_text(json.dumps({"schema_version":1,"base_currency":"SEK","overlap_sessions":20,"max_daily_requests":25,"reserve_daily_requests":10,"assets":[{"asset_id":"US:IBM","yahoo_symbol":"IBM","alpha_symbol":"IBM","name":"IBM","venue":"NYSE","currency":"USD","required":True}]}))
  import kvant_console.api as api;importlib.reload(api)
  from kvant_console.alpha import Client
  def fake_daily(self,asset,full=False):
   bars=[]
   from datetime import date,timedelta
   for i in range(140):
    d=date(2024,1,1)+timedelta(days=i);price=100+i*.1;bars.append({"asset_id":asset.asset_id,"date":d,"open":price,"high":price+1,"low":price-1,"close":price+.2,"adjusted":price+.2,"volume":1000+i,"retrieved_at":datetime.now(timezone.utc),"hash":"fixture"})
   return bars,[]
  monkeypatch.setattr(Client,"daily",fake_daily);client=TestClient(api.app)
  assert client.put("/api/universe",json=json.loads(settings.CONFIG.read_text())).status_code==200
  assert client.post("/api/data/bootstrap/alpha").status_code==200
  assert client.get("/api/data/freshness").json()[0]["rows"]==140
  assert client.post("/api/models/baseline").status_code==200
  assert client.post("/api/backtests").status_code==200
  assert client.get("/api/paper/portfolio").status_code==200
  audit=client.post("/api/audit/export").json();assert Path(audit["path"]).exists()
