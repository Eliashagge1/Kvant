import hashlib,os,time
from datetime import date,datetime,timezone
from decimal import Decimal
import requests
from .core import Bar,Action
class AlphaClient:
 def __init__(self,key=None,session=None):
  self.key=key or os.getenv('ALPHAVANTAGE_API_KEY');self.http=session or requests.Session()
  if not self.key:raise RuntimeError('ALPHAVANTAGE_API_KEY required')
 def load(self,symbol,outputsize):
  p={'function':'TIME_SERIES_DAILY_ADJUSTED','symbol':symbol.provider_symbol,'outputsize':outputsize,'apikey':self.key}
  for attempt in range(3):
   response=self.http.get('https://www.alphavantage.co/query',params=p,timeout=30);text=response.text
   if response.status_code==200:
    data=response.json()
    if not any(k in data for k in ('Note','Information','Error Message')):break
   if attempt==2:raise RuntimeError('Alpha Vantage failed or rate limited')
   time.sleep(2**attempt)
  series=data.get('Time Series (Daily)');
  if not isinstance(series,dict):raise RuntimeError('missing daily series')
  now=datetime.now(timezone.utc);digest=hashlib.sha256(text.encode()).hexdigest();bars=[];actions=[]
  for ds,row in series.items():
   d=date.fromisoformat(ds);b=Bar(symbol.asset_id,d,Decimal(row['1. open']),Decimal(row['2. high']),Decimal(row['3. low']),Decimal(row['4. close']),Decimal(row['6. volume']),'alpha_vantage',now,digest,Decimal(row['5. adjusted close']))
   if min(b.open,b.high,b.low,b.close)<=0 or b.volume<0 or b.high<max(b.open,b.close,b.low) or b.low>min(b.open,b.close,b.high):raise RuntimeError(f'invalid OHLCV {ds}')
   bars.append(b);div=Decimal(row.get('7. dividend amount','0'));split=Decimal(row.get('8. split coefficient','1'))
   if div:actions.append(Action(f'av:div:{symbol.asset_id}:{ds}',symbol.asset_id,'cash_dividend',d,now,'alpha_vantage',digest,div,symbol.currency,None))
   if split!=1:actions.append(Action(f'av:split:{symbol.asset_id}:{ds}',symbol.asset_id,'split',d,now,'alpha_vantage',digest,None,None,split))
  return sorted(bars,key=lambda b:b.session_date),actions
