from datetime import datetime,timezone
class Paper:
    def __init__(self,db):self.db=db
    def ensure(self):
        if not self.db.c.execute("SELECT count(*) FROM paper_cash").fetchone()[0]:self.db.c.execute("INSERT INTO paper_cash VALUES ('SEK',100000)")
    def snapshot(self):
        self.ensure();cash=self.db.c.execute("SELECT currency,amount FROM paper_cash").fetchall();positions=self.db.c.execute("SELECT asset_id,quantity,average_price,last_price,updated_at FROM paper_positions").fetchall();equity=sum(x[1] for x in cash)+sum(x[1]*x[3] for x in positions);return {"cash":[{"currency":c,"amount":a} for c,a in cash],"positions":[{"asset_id":a,"quantity":q,"average_price":p,"last_price":l,"updated_at":str(t)} for a,q,p,l,t in positions],"equity_sek":equity}
    def mark_from_canonical(self):
        self.ensure();rows=self.db.c.execute("SELECT p.asset_id,p.quantity,b.close FROM paper_positions p JOIN (SELECT asset_id,arg_max(close,session_date) close FROM raw_bars WHERE canonical=true GROUP BY asset_id)b USING(asset_id)").fetchall()
        for a,_,price in rows:self.db.c.execute("UPDATE paper_positions SET last_price=?,updated_at=current_timestamp WHERE asset_id=?",[price,a])
