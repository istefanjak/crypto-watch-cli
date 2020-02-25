import os

def findCoin(coins, **kwarg):
    if len(kwarg) != 1:
        raise Exception("Use only 1 kwarg!")
    key = list(kwarg)[0]
    val = kwarg[key]
    for coin in coins:
        if eval(f"str(coin.{key}).lower()") == str(val).lower():
            return coin

def cls():
    os.system('cls' if os.name=='nt' else 'clear')