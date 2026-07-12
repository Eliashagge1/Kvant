import tempfile
from pathlib import Path
from datetime import date,datetime,timezone
from decimal import Decimal
from kvant_data.core import Bar,Action
from kvant_data.store import Store
from kvant_data.adjust import rebuild
def b(d,c):return Bar('A',date.fromisoformat(d),Decimal(c),Decimal(c),Decimal(c),Decimal(c),Decimal(100),'alpha_vantage',datetime.now(timezone.utc),'h',Decimal(c))
def test_atomic_and_adjusted():
 with tempfile.TemporaryDirectory() as td:
  s=Store(Path(td)/'x.db');bars=[b('2024-01-01','100'),b('2024-01-02','102'),b('2024-01-03','51')];action=Action('split','A','split',date(2024,1,3),datetime.now(timezone.utc),'alpha_vantage','h',None,None,Decimal(2));s.commit_batch('ok',['A'],{'A':(bars,[action])});rebuild(s,'A');assert s.db.execute('select count(*) from adjusted_series').fetchone()[0]==3
  try:s.commit_batch('bad',['A','B'],{'A':(bars,[action])});assert False
  except RuntimeError:pass
