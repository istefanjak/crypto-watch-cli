from controller import ApiRequest, Printer
from datafactory import Portfolio, Tokener, IntegrityException
import sys
import argparse
import util
from time import sleep
from const import WATCH_REFRESH

class Main:
    def __init__(self):
        self.tokener = Tokener()

        self.apiRequest = ApiRequest()
        tokenerRet = self.tokener.read()
        if tokenerRet:
            self.apiRequest.setApiToken(tokenerRet)

        self.portfolio = Portfolio()
        self.printer = Printer()
        self.printerInit()

        self.parserMain = argparse.ArgumentParser()
        subparsers = self.parserMain.add_subparsers(title="Subcommands", required=True, dest="cmd")
        self.insertSubparserInit(subparsers)
        self.removeSubparserInit(subparsers)
        self.purgeSubparserInit(subparsers)
        self.watchSubparserInit(subparsers)
        self.settokenSubparserInit(subparsers)

    def parse(self):
        args = self.parserMain.parse_args()
        args.func(args)

    def printerInit(self):
        self.printer.addColumn("Holdings", self.portfolio.getHoldings, coin=True)
        self.printer.addColumn("Holdings value $", self.portfolio.getValueUSD, coin=True, usdtotal=True, _format="${:.8f}")
        self.printer.addColumn("Holdings value BTC", self.portfolio.getValueBTC, coin=True, btctotal=True, _format="{:.8f} BTC")

    def insertSubparserInit(self, subparser):
        parser = subparser.add_parser("insert", help="Insert a crypto asset into portfolio")

        tmpGroup = parser.add_argument_group(title="Required options (choose 1)")
        groupRequired = tmpGroup.add_mutually_exclusive_group(required=True)
        groupRequired.add_argument("-n", "--name", help="Currency name")
        groupRequired.add_argument("-s", "--symbol", help="Currency symbol")
        groupRequired.add_argument("-i", "--id", help="Currency ID")

        groupOptional = parser.add_argument_group(title="Optional arguments")
        groupOptional.add_argument("--holdings", type=float, default=0, help="Number of holdings, default 0")
        parser.set_defaults(func=self.insert)

    def removeSubparserInit(self, subparser):
        parser = subparser.add_parser("remove", help="Remove a currency from portfolio by ID")

        groupRequired = parser.add_argument_group(title="Required arguments")
        groupRequired.add_argument("id", help="Currency ID")
        parser.set_defaults(func=self.remove)

    def purgeSubparserInit(self, subparser):
        parser = subparser.add_parser("purge", help="Purge the portfolio")
        parser.set_defaults(func=self.purge)
    
    def watchSubparserInit(self, subparser):
        parser = subparser.add_parser("watch", help="Watch the portfolio")
        parser.set_defaults(func=self.watch)

    def settokenSubparserInit(self, subparser):
        parser = subparser.add_parser("settoken", help="Set the Coinmarketcap API token")
        groupRequired = parser.add_argument_group(title="Required arguments")
        groupRequired.add_argument("token")
        parser.set_defaults(func=self.settoken)

    def insert(self, args):
        if not self.apiRequest.isTokenSet:
            print("Please set your token first! Use settoken CMD")
            sys.exit(1)
        if args.name:
            textHolder = "slug"
            valueHolder = args.name
            coins = self.apiRequest.request(coinNames=[args.name])
        elif args.symbol:
            textHolder = "symbol"
            valueHolder = args.symbol
            coins = self.apiRequest.request(coinSymbols=[args.symbol])
        else:
            textHolder = "id"
            valueHolder = args.id
            coins = self.apiRequest.request(coinIds=[args.id])

        _match = util.findCoin(coins, **{textHolder:valueHolder})
        if _match is None:
            print("Error finding the cryptocurrency.\nNothing inserted.")
            sys.exit(2)

        try:
            self.portfolio.insert(_match.id, args.holdings)

        except IntegrityException:
            print(f"Error: coin with {textHolder} {valueHolder} already in portfolio.")
            print(f"Do you wish to update the holdings of the coin to {args.holdings} in your potfolio?")
            while True:
                inputVals = {"Y": True, "N": False}
                userInput = input("Y / N: ").upper()
                if userInput in inputVals:
                    break
            if not inputVals[userInput]:
                return
            try:
                self.portfolio.insert(_match.id, args.holdings, onIntegrityFailDoUpdate=True)
            except IntegrityException:
                pass

        print(f"Currency with {textHolder} {valueHolder}, holdings {args.holdings} inserted successfully into portfolio!")
    
    def remove(self, args):
        try:
            ret = self.portfolio.remove(args.id)
            if not ret:
                print(f"Error: Cryptocurrency with id {args.id} not found in potfolio!")
                if int(args.id) == 1:
                    print("Please note that bitcoin is always being displayed in your watches, although it may not be in your potfolio!")
            else:
                print(f"Cryptocurrency with id {args.id} successfully removed from portfolio!")
        except Exception:
            print(f"Error removing cryptocurrency with id {args.id} from portfolio!")
    
    def purge(self, args):
        try:
            self.portfolio.removeAll()
            print("Portfolio successfully purged!")
        except Exception:
            print("Error purging portfolio!")

    def watch(self, args):
        if not self.apiRequest.isTokenSet:
            print("Please set your token first! Use settoken CMD")
            sys.exit(1)

        coins = None
        try:
            while True:
                if coins is None or cnt == WATCH_REFRESH:
                    cnt = 0
                    coins = self.apiRequest.request(coinIds=[str(row["id"]) for row in self.portfolio])
                    util.cls()
                    self.printer.print(coins)

                self.printer.printTime(cnt)
                print("\r", end="")
                sleep(1)
                cnt += 1
        
        except KeyboardInterrupt:
            print("\r\n\n Keyboard interrupt: Exiting...")
            sys.exit(0)

    
    def settoken(self, args):
        self.tokener.write(args.token)
        self.apiRequest.setApiToken(args.token)


if __name__ == "__main__":
    _main = Main()
    _main.parse()