from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from .common import atomic_parquet,validate_membership,validate_prices,write_manifest

def main():
 p=argparse.ArgumentParser(description="Normalize licensed Sharadar bulk exports")
 p.add_argument("--sep",required=True);p.add_argument("--tickers",required=True);p.add_argument("--membership");p.add_argument("--output",required=True);a=p.parse_args()
 sep=pd.read_csv(a.sep,low_memory=False);tickers=pd.read_csv(a.tickers,low_memory=False)
 status=tickers.get("isdelisted",pd.Series(False,index=tickers.index)).astype(bool)
 ticker_meta=tickers.assign(is_delisted=status)[["ticker","is_delisted"]].drop_duplicates("ticker")
 prices=sep.merge(ticker_meta,on="ticker",how="left",validate="many_to_one")
 prices=prices.rename(columns={"ticker":"ticker","date":"date","open":"open","high":"high","low":"low","close":"close","volume":"volume"})
 prices["asset_id"]=prices["ticker"];prices["is_delisted"]=prices["is_delisted"].fillna(False)
 prices=validate_prices(prices[["asset_id","ticker","date","open","high","low","close","volume","is_delisted"]])
 out=Path(a.output);out.mkdir(parents=True,exist_ok=True);atomic_parquet(prices,out/"prices.parquet");inputs=[a.sep,a.tickers];counts={"prices":len(prices)}
 if a.membership:
  m=pd.read_csv(a.membership);m=m.rename(columns={"ticker":"ticker","index":"index_id","start":"start_date","end":"end_date"});m["asset_id"]=m["ticker"];m=validate_membership(m[["asset_id","ticker","index_id","start_date","end_date"]]);atomic_parquet(m,out/"universe_membership.parquet");inputs.append(a.membership);counts["membership"]=len(m)
 write_manifest(out,"sharadar",inputs,counts)
if __name__=="__main__":main()
