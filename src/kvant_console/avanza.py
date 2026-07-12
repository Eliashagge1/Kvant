import csv,io,json,re,uuid
from decimal import Decimal,InvalidOperation
ALIASES={"date":["datum","date","transaktionsdatum"],"kind":["typ av transaktion","transaktionstyp","typ","transaction"],"asset":["värdepapper/beskrivning","värdepapper","instrument","description"],"amount":["belopp","amount"],"currency":["valuta","currency"]}
def norm(s):return re.sub(r"\s+"," ",s.strip().lower())
def parse_number(s):
    s=(s or "").replace(" ","").replace(" ","").replace(".","").replace(",",".")
    try:return float(Decimal(s))
    except InvalidOperation:return None
def parse(content:bytes):
    text=content.decode("utf-8-sig",errors="replace");dialect=csv.Sniffer().sniff(text[:4096],delimiters=";,	,");rows=list(csv.DictReader(io.StringIO(text),dialect=dialect));headers={norm(h):h for h in (rows[0].keys() if rows else [])}
    def find(k):
        for a in ALIASES[k]:
            if norm(a) in headers:return headers[norm(a)]
        return None
    mapping={k:find(k) for k in ALIASES};missing=[k for k,v in mapping.items() if not v]
    if missing:raise ValueError(f"unsupported Avanza CSV; missing semantic columns: {missing}")
    out=[]
    for i,r in enumerate(rows,2):out.append({"row_number":i,"date":r[mapping['date']],"kind":r[mapping['kind']],"asset":r[mapping['asset']],"amount":parse_number(r[mapping['amount']]),"currency":r[mapping['currency']],"raw":r})
    return out
def reconcile(db,content):
    rows=parse(content);run=str(uuid.uuid4());unknown={"okänd","unknown",""}
    with db.tx():
        for r in rows:
            status="review" if norm(r["kind"]) in unknown or r["amount"] is None else "parsed"
            db.c.execute("INSERT INTO reconciliation VALUES (?,?,?,?,?,?,?,?)",[run,r["row_number"],status,r["kind"],r["asset"],r["amount"],r["currency"],json.dumps(r["raw"],ensure_ascii=False)])
            if status=="review":db.c.execute("INSERT INTO review_queue VALUES (?,current_timestamp,'avanza_csv',?,'warning',?,?, 'open',NULL,NULL)",[str(uuid.uuid4()),r["asset"],f"Unrecognized or incomplete transaction type: {r['kind']}",json.dumps(r["raw"],ensure_ascii=False)])
    return {"run_id":run,"rows":len(rows),"parsed":sum(r["amount"] is not None for r in rows),"review":sum(r["amount"] is None or norm(r["kind"]) in unknown for r in rows)}
