from datetime import datetime,timezone,date
import requests,hashlib
from .secrets import get_alpha_key
BASE="https://www.alphavantage.co/query"
class AlphaError(RuntimeError): pass
class Client:
    def __init__(self,key=None,session=None): self.key=key or get_alpha_key(); self.s=session or requests.Session()
    def _get(self,params):
        p={**params,"apikey":self.key};r=self.s.get(BASE,params=p,timeout=30)
        if r.status_code!=200: raise AlphaError(f"HTTP {r.status_code}")
        x=r.json()
        for k in ("Error Message","Note","Information"):
            if k in x: raise AlphaError(str(x[k]))
        return x,r.text
    def search(self,keywords):
        x,_=self._get({"function":"SYMBOL_SEARCH","keywords":keywords})
        return [{"symbol":m.get("1. symbol"),"name":m.get("2. name"),"type":m.get("3. type"),"region":m.get("4. region"),"currency":m.get("8. currency"),"match_score":m.get("9. matchScore")} for m in x.get("bestMatches",[])]
    def daily(self,asset,full=False):
        x,text=self._get({"function":"TIME_SERIES_DAILY_ADJUSTED","symbol":asset.alpha_symbol,"outputsize":"full" if full else "compact"})
        series=x.get("Time Series (Daily)")
        if not isinstance(series,dict): raise AlphaError("missing Time Series (Daily)")
        now=datetime.now(timezone.utc);h=hashlib.sha256(text.encode()).hexdigest();bars=[];actions=[]
        for ds,row in series.items():
            b={"asset_id":asset.asset_id,"date":date.fromisoformat(ds),"open":float(row["1. open"]),"high":float(row["2. high"]),"low":float(row["3. low"]),"close":float(row["4. close"]),"adjusted":float(row["5. adjusted close"]),"volume":float(row["6. volume"]),"retrieved_at":now,"hash":h}
            if min(b["open"],b["high"],b["low"],b["close"])<=0 or b["high"]<max(b["open"],b["close"],b["low"]) or b["low"]>min(b["open"],b["close"],b["high"]): raise AlphaError(f"invalid OHLC {ds}")
            bars.append(b);div=float(row.get("7. dividend amount",0));split=float(row.get("8. split coefficient",1))
            if div: actions.append((f"av:div:{asset.asset_id}:{ds}",asset.asset_id,"cash_dividend",b["date"],now,"alpha_vantage",h,div,asset.currency,None))
            if split!=1: actions.append((f"av:split:{asset.asset_id}:{ds}",asset.asset_id,"split",b["date"],now,"alpha_vantage",h,None,None,split))
        return sorted(bars,key=lambda z:z["date"]),actions
