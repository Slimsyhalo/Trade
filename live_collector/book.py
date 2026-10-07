from decimal import Decimal

class BookGap(ValueError): pass

class OrderBook:
    def __init__(self): self.valid=False; self.last=None; self.bids={}; self.asks={}; self.bridged=False
    def snapshot(self,s):
        self.last=s['lastUpdateId']; self.bids={p:q for p,q in s['bids']}; self.asks={p:q for p,q in s['asks']}; self.bridged=False; self.valid=False
    def update(self,e):
        if self.last is None: raise BookGap('Snapshot required')
        if e['u']<self.last or (self.bridged and e['u']==self.last): return False
        if not self.bridged:
            if not e['U']<=self.last<=e['u']: self.valid=False; raise BookGap('Snapshot bridge missing')
        elif e['pu']!=self.last:
            self.valid=False; raise BookGap('Depth pu sequence gap')
        for side,key in ((self.bids,'b'),(self.asks,'a')):
            for price,qty in e[key]:
                if Decimal(qty)==0: side.pop(price,None)
                else: side[price]=qty
        self.last=e['u']; self.bridged=True; self.valid=True; return True
