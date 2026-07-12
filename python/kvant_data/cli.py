import argparse
from .config import Config
from .store import Store
from .pipeline import run
from .yahoo import bootstrap
from .adjust import rebuild as rebuild_one
def parse():
 p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--database');p.add_argument('--output');return p.parse_args()
def bootstrap_alpha():a=parse();c=Config(a.config);s=Store(a.database);run(c,s,True)
def update_daily():a=parse();c=Config(a.config);s=Store(a.database);run(c,s,False)
def bootstrap_yahoo():a=parse();c=Config(a.config);bootstrap(c.symbols,a.output)
def rebuild():a=parse();c=Config(a.config);s=Store(a.database);[rebuild_one(s,x.asset_id) for x in c.symbols]
