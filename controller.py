from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from entity.response import Status, Coin
from error.errors import ApiResponseError
import json
from tabulate import tabulate
from datetime import datetime
import datafactory as df
import sys

class ApiRequest:
    def __init__(self):
        self.url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        self.headers = {
            "Accept-Encoding": "deflate, gzip",
            "Accepts": "application/json"
        }
        self.parameters = {
            "convert": "USD"
        }
        self.session = Session()
        self.isTokenSet = False
    
    def setApiToken(self, API_TOKEN):
        self.headers.update({"X-CMC_PRO_API_KEY": API_TOKEN})
        self.session.headers.update(self.headers)
        self.isTokenSet = True

    def request(self, coinIds: [str]=[], coinSymbols: [str]=[], coinNames: [str]=[]) -> [Coin]:
        btcPrice = "NaN"
        coinList = []
        if len(coinIds):
            coinIds.append("1")
            self.parameters.update(id=",".join(coinIds))
        elif len(coinNames):
            coinNames.append("bitcoin")
            self.parameters.update(slug=",".join([s.lower() for s in coinNames]))
        else:
            coinSymbols.append("BTC")
            self.parameters.update(symbol=",".join([s.upper() for s in coinSymbols]))
        try:
            response = self.session.get(self.url, params=self.parameters)
            data = json.loads(response.text)
            status = Status(**data["status"])
            if status.error_code != 0:
                raise ApiResponseError(f"Error: {status.error_code} {status.error_message}")
            coinList = [Coin(**data["data"][coin]) for coin in data["data"]]
            for coin in coinList:
                if coin.id == 1:
                    btcPrice = coin.price
                    break
            if btcPrice != "NaN":
                for coin in coinList:
                    coin.priceBTC = 1 / btcPrice * coin.price

        except (ConnectionError, Timeout, TooManyRedirects, ApiResponseError) as e:
            print(e)
            sys.exit(1)
        
        return coinList

class Printer:
    def __init__(self):
        self.tableHeaders = ["ID", "Name", "Symbol", "Price USD", "Price BTC"]
        self.dataFactory = {}

    def addColumn(self, name: str, dataFactory, **kwargs):
        self.dataFactory.update({name: (dataFactory, kwargs)})

    def print(self, coins: [Coin]):
        tableHeaders = ["ID", "Name", "Symbol", "Price USD", "Price BTC"]
        startPos = len(tableHeaders) if len(self.dataFactory) else None
        tableHeaders += list(self.dataFactory)
        tableData = []
        cntrs = {"price": 0, "priceBTC": 0}
        for coin in coins:
            row = (coin.id, coin.name, coin.symbol, "${:.8f}".format(coin.price), "{:.8f} BTC".format(coin.priceBTC))
            if startPos is not None:
                tmp = tableHeaders[startPos:]
                for key in tmp:
                    fun = self.dataFactory[key]

                    if "coin" in fun[1]:
                        fun[1].update(coin=coin)
                    usdtotal = fun[1].pop("usdtotal", False)
                    btctotal = fun[1].pop("btctotal", False)
                    _format = fun[1].pop("_format", None)

                    funRet = fun[0](**fun[1])
                    if usdtotal:
                        cntrs["price"] += funRet
                    if btctotal:
                        cntrs["priceBTC"] += funRet
                    if _format is not None:
                        funRet = _format.format(funRet)
                    row += (funRet,)

                    fun[1].update(usdtotal=usdtotal)
                    fun[1].update(btctotal=btctotal)
                    fun[1].update(_format=_format)
            tableData.append(row)
        print(tabulate(tableData, headers=tableHeaders, tablefmt="github"))
        print()
        print()
        self.__printTotal_helper(cntrs["price"], cntrs["priceBTC"])
        print()

    def __printTotal_helper(self, totalUSD, totalBTC):
        tableHeaders = ["", "Total"]
        rows = [ ("USD", "${:.8f}".format(totalUSD)), ("BTC", "{:.8f} BTC".format(totalBTC)) ]
        print(tabulate(rows, headers=tableHeaders, tablefmt="github"))
    
    def printTime(self, time):
        time = datetime.fromtimestamp(time).strftime("%Mm %Ss")
        print(f"Time since refresh: {time}", end="")