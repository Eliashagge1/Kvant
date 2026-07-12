from pydantic import BaseModel, Field, model_validator
from pathlib import Path
import json, os, tempfile
class Asset(BaseModel):
    asset_id:str; yahoo_symbol:str; alpha_symbol:str; name:str=""; venue:str; currency:str; required:bool=True
class Universe(BaseModel):
    schema_version:int=1; base_currency:str="SEK"; overlap_sessions:int=90
    max_daily_requests:int=25; reserve_daily_requests:int=10; benchmark_asset_id:str|None=None
    assets:list[Asset]=Field(default_factory=list)
    @model_validator(mode="after")
    def valid(self):
        ids=[x.asset_id for x in self.assets]
        if len(ids)!=len(set(ids)): raise ValueError("duplicate asset_id")
        if sum(x.required for x in self.assets)>self.max_daily_requests-self.reserve_daily_requests: raise ValueError("required universe exceeds safe quota")
        if self.overlap_sessions<20: raise ValueError("overlap_sessions must be at least 20")
        return self
def load(path:Path)->Universe:
    if not path.exists(): return Universe()
    return Universe.model_validate_json(path.read_text())
def save(path:Path,u:Universe):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=path.parent,prefix=path.name,suffix=".tmp")
    try:
        with os.fdopen(fd,"w") as f: f.write(u.model_dump_json(indent=2)); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
