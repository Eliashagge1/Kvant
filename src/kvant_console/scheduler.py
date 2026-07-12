import argparse,fcntl,os,time
from datetime import datetime
from pathlib import Path
from . import settings
from .cli import daily
def main():
 p=argparse.ArgumentParser();p.add_argument("--hour",type=int,default=19);p.add_argument("--minute",type=int,default=0);a=p.parse_args();settings.ensure_dirs();lock=open(settings.HOME/"scheduler.lock","w")
 try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:raise SystemExit("scheduler already running")
 last=None
 while True:
  now=datetime.now();key=now.date()
  if now.hour==a.hour and now.minute>=a.minute and last!=key:
   try:daily();last=key
   except Exception as e:print(f"FAIL-CLOSED {now.isoformat()} {e}",flush=True)
  time.sleep(30)
