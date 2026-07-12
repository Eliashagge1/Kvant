import hashlib,json,uuid
import numpy as np,pandas as pd
from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import TimeSeriesSplit

def run_baselines(db,git_commit="unknown"):
    df=db.c.execute("SELECT asset_id,session_date,total_return_index FROM adjusted_series ORDER BY asset_id,session_date").df();rows=[]
    for _,g in df.groupby("asset_id"):
        g=g.copy();g["r1"]=g.total_return_index.pct_change();g["mom5"]=g.total_return_index.pct_change(5);g["vol20"]=g.r1.rolling(20).std();g["target"]=g.r1.shift(-1);rows.append(g)
    data=pd.concat(rows).dropna();X=data[["r1","mom5","vol20"]].to_numpy();y=data.target.to_numpy()
    if len(y)<80:raise RuntimeError("insufficient adjusted history for baseline modelling")
    models={"Historical mean":None,"Ridge":Ridge(alpha=1.0),"Gradient tree":HistGradientBoostingRegressor(max_depth=3,random_state=42)};results=[];ts=TimeSeriesSplit(5)
    for name,model in models.items():
        preds=np.zeros_like(y);mask=np.zeros(len(y),bool)
        for tr,te in ts.split(X):
            pred=np.full(len(te),y[tr].mean()) if model is None else model.fit(X[tr],y[tr]).predict(X[te]);preds[te]=pred;mask[te]=True
        mse=mean_squared_error(y[mask],preds[mask]);ic=float(np.corrcoef(y[mask],preds[mask])[0,1]);strategy=np.sign(preds[mask])*y[mask];sharpe=float(strategy.mean()/strategy.std(ddof=1)*np.sqrt(252)) if strategy.std(ddof=1)>0 else 0;results.append((name,float(mse),ic,sharpe))
    run=str(uuid.uuid4());selected=min(results,key=lambda x:x[1])[0];payload=json.dumps(results,sort_keys=True);h=hashlib.sha256(payload.encode()).hexdigest()
    with db.tx():
        db.c.execute("INSERT INTO experiments VALUES (?,current_timestamp,?,?,?,?,?,?,?)",[run,git_commit,"canonical-duckdb","features-v1",h,json.dumps({"splits":5}),json.dumps({"selected":selected}),len(results)])
        db.c.executemany("INSERT INTO model_results VALUES (?,?,?,?,?,?)",[[run,*x,x[0]==selected] for x in results])
    return {"run_id":run,"selected":selected,"results":[{"model":n,"mse":m,"ic":i,"sharpe":s,"selected":n==selected} for n,m,i,s in results]}

def run_backtest(db):
    run=str(uuid.uuid4());df=db.c.execute("SELECT session_date,avg(total_return_index) tri FROM adjusted_series GROUP BY session_date ORDER BY session_date").df();r=df.tri.pct_change().fillna(0);signal=np.sign(r.rolling(20).mean().shift(1).fillna(0));gross=signal*r;turnover=signal.diff().abs().fillna(0);cost=turnover*.0008;net=gross-cost;equity=(1+net).cumprod()*100000;benchmark=(1+r).cumprod()*100000
    db.c.executemany("INSERT INTO backtest_daily VALUES (?,?,?,?,?,?)",[[run,d,float(e),float(b),float(x),float(c)] for d,e,b,x,c in zip(df.session_date,equity,benchmark,net,cost)])
    return {"run_id":run,"ending_equity":float(equity.iloc[-1]),"return_pct":float(equity.iloc[-1]/equity.iloc[0]-1)*100,"sharpe":float(net.mean()/net.std(ddof=1)*np.sqrt(252)) if net.std(ddof=1)>0 else 0,"max_drawdown_pct":float((equity/equity.cummax()-1).min()*100)}
