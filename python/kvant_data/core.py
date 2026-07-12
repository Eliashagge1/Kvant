from dataclasses import dataclass
from datetime import date,datetime
from decimal import Decimal
@dataclass(frozen=True)
class Symbol: asset_id:str;provider_symbol:str;display_symbol:str;venue:str;currency:str;required:bool=True
@dataclass(frozen=True)
class Bar: asset_id:str;session_date:date;open:Decimal;high:Decimal;low:Decimal;close:Decimal;volume:Decimal;provider:str;retrieved_at:datetime;payload_hash:str;vendor_adjusted_close:Decimal|None=None
@dataclass(frozen=True)
class Action: event_id:str;asset_id:str;event_type:str;ex_date:date;available_at:datetime;provider:str;payload_hash:str;cash_amount:Decimal|None=None;currency:str|None=None;split_coefficient:Decimal|None=None
