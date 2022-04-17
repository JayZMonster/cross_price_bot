from binance import Client
from binance.exceptions import *
from typing import List


class BinanceParser:

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client: Client
        self._init_client()

    def _init_client(self):
        self.client = Client(self.api_key, self.api_secret)

    def get_cost(self, ticker='USDTRUB'):
        """
        Getting ticker's last price
        """
        try:
            ticker = self.client.get_ticker(symbol=ticker)
            return ticker['lastPrice']
        except BinanceAPIException as e:
            print(e)

    def get_all_tickers(self, _tickers: List[dict]):
        """
        Generating list of ticker's prices
        """
        all_prices = []
        for ticker in _tickers:
            semi_ticker = ticker['ticker']['ticker']
            full_ticker = semi_ticker + 'USDT'
            price = self.get_cost(full_ticker)
            info = {'ticker': semi_ticker, 'price': price}
            all_prices.append(info)
        return all_prices


#if __name__ == '__main__':
 #   bp = BinanceParser('', '')
  #  tickers = [{
   #     'ticker': {
   #         'ticker': 'BCH'
   #     }
   # }]
   # print(bp.get_usd_p2p())
