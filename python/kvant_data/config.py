import json
from .core import Symbol
class Config:
 def __init__(self,path):
  x=json.load(open(path));self.base_currency=x['base_currency'];self.overlap_sessions=int(x.get('overlap_sessions',90));self.max_daily_requests=int(x.get('max_daily_requests',25));self.reserve=int(x.get('reserve_daily_requests',10));self.symbols=[Symbol(**s) for s in x['symbols']]
  if x.get('schema_version')!=1 or not self.symbols:raise ValueError('invalid config')
  if len([s for s in self.symbols if s.required])>self.max_daily_requests-self.reserve:raise ValueError('universe exceeds safe request budget')
  if len({s.asset_id for s in self.symbols})!=len(self.symbols):raise ValueError('duplicate asset ID')
