import uuid
from .alpha import AlphaClient
from .adjust import rebuild
def run(config,store,full=False,client=None):
 client=client or AlphaClient();results={};errors={}
 for s in config.symbols:
  try:results[s.asset_id]=client.load(s,'full' if full else 'compact')
  except Exception as e:errors[s.asset_id]=str(e)
 required=[s.asset_id for s in config.symbols if s.required]
 if set(required)-set(results):
  store.db.execute("INSERT INTO data_batches VALUES (?,current_timestamp,current_timestamp,'rejected',?,?,?)",[f'rejected-{uuid.uuid4()}',len(required),len(results),str(errors)]);raise RuntimeError(f'atomic update rejected: {errors}')
 store.commit_batch(f"{'bootstrap' if full else 'daily'}-{uuid.uuid4()}",required,results)
 for s in config.symbols:rebuild(store,s.asset_id)
