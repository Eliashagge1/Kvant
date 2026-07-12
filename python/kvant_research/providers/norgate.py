from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from .common import atomic_parquet,validate_membership,validate_prices,write_manifest

def main():
 p=argparse.ArgumentParser(description="Normalize licensed Norgate CSV exports produced on the vendor-supported host")
 p.add_argument("--prices",required=True);p.add_argument("--membership",required=True);p.add_argument("--output",required=True);a=p.parse_args()
 raw=pd.read_csv(a.prices,low_memory=False);raw.columns=[c.strip().lower().replace(" ","_") for c in raw.columns]
 aliases={"security_id":"asset_id","symbol":"ticker","unadjusted_close":"close"};raw=raw.rename(columns=aliases)
 if "asset_id" not in raw: raw["asset_id"]=raw["ticker"]
 if "is_delisted" not in raw: raw["is_delisted"]=raw.get("delisted",False)
 prices=validate_prices(raw[["asset_id","ticker","date","open","high","low","close","volume","is_delisted"]])
 membership=pd.read_csv(a.membership);membership.columns=[c.strip().lower().replace(" ","_") for c in membership.columns];membership=membership.rename(columns={"security_id":"asset_id","symbol":"ticker","index":"index_id","entry_date":"start_date","exit_date":"end_date"})
 if "asset_id" not in membership: membership["asset_id"]=membership["ticker"]
 membership=validate_membership(membership[["asset_id","ticker","index_id","start_date","end_date"]])
 out=Path(a.output);out.mkdir(parents=True,exist_ok=True);atomic_parquet(prices,out/"prices.parquet");atomic_parquet(membership,out/"universe_membership.parquet");write_manifest(out,"norgate",[a.prices,a.membership],{"prices":len(prices),"membership":len(membership)})
if __name__=="__main__":main()
