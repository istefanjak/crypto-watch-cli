from tinydb import TinyDB, Query
from const import PORTFOLIO, TOKEN_FILE
import os

class IntegrityException(Exception):
    pass

class Portfolio:
    def __init__(self):
        self.db = TinyDB(PORTFOLIO)
    
    def insert(self, coinID, holdings, onIntegrityFailDoUpdate=False):
        entry = Query()
        check = self.db.search(entry.id == coinID)
        if len(check):
            if not onIntegrityFailDoUpdate:
                raise IntegrityException("Coin already in DB")
            
            self.update(coinID, holdings)
            raise IntegrityException("Coin already in DB")

        self.db.insert({"id": coinID, "holdings": holdings})
    
    def update(self, coinID, newHoldings):
        entry = Query()
        return len(self.db.update({"holdings": newHoldings}, entry.id == coinID))

    def remove(self, coinID):
        coinID = int(coinID)
        entry = Query()
        return len(self.db.remove(entry.id == coinID))
    
    def removeAll(self):
        self.db.purge()

    def __iter__(self):
        for row in self.db:
            yield row

    def getHoldings(self, coin):
        entry = Query()
        result = self.db.search(entry.id == coin.id)
        return result[0]["holdings"] if len(result) else 0
    
    def getValueUSD(self, coin):
        return self.getHoldings(coin) * coin.price
    
    def getValueBTC(self, coin):
        return self.getHoldings(coin) * coin.priceBTC

class Tokener:
    def read(self):
        try:
            with open(TOKEN_FILE) as f:
                data = [d.strip() for d in f.readlines()]
                if len(data) != 1:
                    raise ValueError("token file corrupted")
                return data[0]

        except (IOError, ValueError):
            pass
    
    def write(self, token):
        exists = False
        if os.path.exists(TOKEN_FILE):
            exists = True
        try:
            with open(TOKEN_FILE, "w") as f:
                f.write(token)
                return exists

        except (IOError, ValueError):
            pass

#Driver test
if __name__ == "__main__":
    t = Tokener()
    print(t.write("abc"))