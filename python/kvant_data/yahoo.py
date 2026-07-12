import hashlib,json
from pathlib import Path
import yfinance as yf
def bootstrap(symbols,output):
 out=Path(output);out.mkdir(parents=True,exist_ok=True);manifest={'schema_version':1,'provider':'yfinance','canonical':False,'eligible_for_live_inference':False,'assets':[]}
 for s in symbols:
  df=yf.download(s.provider_symbol,period='max',auto_adjust=False,actions=True,progress=False,threads=False,multi_level_index=False)
  if df.empty:raise RuntimeError(f'no Yahoo data for {s.provider_symbol}')
  df=df.reset_index();df.columns=[str(c).lower().replace(' ','_') for c in df.columns];df['asset_id']=s.asset_id;df['provider']='yfinance';df['canonical']=False;p=out/f"{s.asset_id.replace(':','_')}.parquet";df.to_parquet(p,index=False);manifest['assets'].append({'asset_id':s.asset_id,'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rows':len(df)})
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
