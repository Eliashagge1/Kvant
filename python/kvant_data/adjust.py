import hashlib
from decimal import Decimal,getcontext
getcontext().prec=38
def rebuild(store,asset):
 bars=store.db.execute('SELECT session_date,close FROM raw_bars WHERE asset_id=? AND canonical=true ORDER BY session_date',[asset]).fetchall();acts=store.db.execute("SELECT ex_date,event_type,cash_amount,split_coefficient,event_id FROM corporate_actions WHERE asset_id=? AND review_status='accepted' ORDER BY ex_date,event_id",[asset]).fetchall();by={};ids=[]
 for d,t,c,s,e in acts:by.setdefault(d,[]).append((t,Decimal(str(c)) if c is not None else Decimal(0),Decimal(str(s)) if s is not None else Decimal(1)));ids.append(e)
 factor=Decimal(1);rows=[]
 for d,c in reversed(bars):
  for t,_,s in by.get(d,[]):
   if t=='split':factor*=s
  rows.append([d,Decimal(str(c))/factor,None])
 rows.reverse();tri=Decimal(1);previous=None
 for row in rows:
  d,a,_=row;div=sum((c for t,c,_ in by.get(d,[]) if t=='cash_dividend'),Decimal(0))
  if previous is not None:tri*=(a+div)/previous
  row[2]=tri;previous=a
 h=hashlib.sha256((asset+'|'.join(ids)).encode()).hexdigest()
 with store.tx():store.db.execute('DELETE FROM adjusted_series WHERE asset_id=?',[asset]);store.db.executemany('INSERT INTO adjusted_series VALUES (?,?,?,?,?)',[[asset,d,a,t,h] for d,a,t in rows])
