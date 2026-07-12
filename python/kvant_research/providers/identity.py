TRUE={"1","Y","YES","TRUE","T"};FALSE={"0","N","NO","FALSE","F",""}
def parse_delisted(value):
 s="" if value is None else str(value).strip().upper()
 if s in TRUE:return True
 if s in FALSE:return False
 raise ValueError(f"unknown delisting flag: {value!r}")
def sharadar_asset_id(row):
 for key in ("permaticker","secid","cusips"):
  value=row.get(key)
  if value is not None and str(value).strip():return f"sharadar:{key}:{str(value).strip()}"
 raise ValueError("Sharadar row lacks stable identifier")
def norgate_asset_id(row):
 for key in ("assetid","security_id"):
  value=row.get(key)
  if value is not None and str(value).strip():return f"norgate:{str(value).strip()}"
 raise ValueError("Norgate row lacks stable identifier")
