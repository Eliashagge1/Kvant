from decimal import Decimal
def compare(alpha,yahoo,sessions=90,price_tolerance=Decimal('0.0001'),volume_tolerance=Decimal('0.02')):
 a={x.session_date:x for x in alpha};y={x.session_date:x for x in yahoo};dates=sorted(set(a)&set(y))[-sessions:];issues=[]
 if len(dates)<min(20,sessions):return [{'severity':'critical','classification':'MISSING_OVERLAP','found':len(dates)}]
 for d in dates:
  for f in ('open','high','low','close'):
   av,yv=getattr(a[d],f),getattr(y[d],f)
   if abs(av-yv)/max(abs(av),abs(yv),Decimal(1))>price_tolerance:issues.append({'date':str(d),'field':f,'severity':'critical','classification':'OHLC_MISMATCH','alpha':str(av),'yahoo':str(yv)})
  if abs(a[d].volume-y[d].volume)/max(a[d].volume,y[d].volume,Decimal(1))>volume_tolerance:issues.append({'date':str(d),'field':'volume','severity':'warning','classification':'VOLUME_CONVENTION'})
 return issues
