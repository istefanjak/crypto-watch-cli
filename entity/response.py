class Status:
    def __init__(self, **kwargs):
        try:
            self.timestamp = kwargs.pop("timestamp")
            self.error_code = kwargs.pop("error_code")
            self.error_message = kwargs.pop("error_message")
            self.elapsed = kwargs.pop("elapsed")
            self.credit_count = kwargs.pop("credit_count")
            self.notice = kwargs.pop("notice")
        except KeyError as e:
            print(f"Warning: (Status) JSON key {e} not found.")

class Coin:
    def __init__(self, **kwargs):
        try:
            self.id = kwargs.pop("id")
            self.name = kwargs.pop("name")
            self.symbol = kwargs.pop("symbol")
            self.slug = kwargs.pop("slug")
            self.num_market_pairs = kwargs.pop("num_market_pairs")
            self.date_added = kwargs.pop("date_added")
            self.tags = kwargs.pop("tags")
            self.max_supply = kwargs.pop("max_supply")
            self.circulating_supply = kwargs.pop("circulating_supply")
            self.total_supply = kwargs.pop("total_supply")
            self.platform = kwargs.pop("platform")
            self.cmc_rank = kwargs.pop("cmc_rank")
            self.last_updated = kwargs.pop("last_updated")
            self.price = kwargs.pop("quote").pop("USD").pop("price")
            self.priceBTC = None
        except KeyError as e:
            print(f"Warning: (Status) JSON key {e} not found.")
    
    def __str__(self):
        return f"ID: {self.id} | Name: {self.name} | Symbol: {self.symbol} | Price: {self.price} USD"