from datetime import datetime, time, timedelta
import json
from django.http.response import Http404
import requests
import websocket
import finnhub
import pandas as pd
import yfinance as yf
from StockWatcher.lib.helpers.stockWatcher.Messaging.Messaging import TwilioMessenger

import os

from yahoofinancials import YahooFinancials
from django.core import serializers
from mainApp.models import Ticker, TickerWatcher
from django.shortcuts import get_object_or_404, render

FINNHUB_KEY = os.environ['FINNHUB_KEY']
POLYGON_KEY = os.environ['POLYGON_KEY']

# FINNHUB STOCK DATA
finnhub_client = finnhub.Client(api_key=FINNHUB_KEY)

# POLYGON STOCK DATA
finnhub_headers = {
  'Authorization': f'Bearer {POLYGON_KEY}'
}

# IEX STOCK DATA
import pandas as pd
from iexfinance.stocks import Stock
from datetime import datetime
import matplotlib.pyplot as plt
from iexfinance.stocks import get_historical_data

# TWILIO MESSAGING SERVICE
twilio = TwilioMessenger()
class LivePriceUpdate():
  def __init__(self, symbol = '', symbols = []):
    self.symbol = symbol
    self.symbols = symbols
    self.tickers = Ticker.objects.all()
    self.ticker_watchers = TickerWatcher.objects.all()

    self.yahoo_financials = YahooFinancials(self.symbol)

  def syncProdData(self):
    prod_url = 'https://vast-crag-37829.herokuapp.com/search/'
    tickers_url = prod_url + 'tickers/'
    ticker_watchers_url = prod_url + 'ticker_watchers/'

    tickers_response = requests.get(tickers_url)
    time.sleep(1)
    ticker_watchers_response = requests.get(ticker_watchers_url)

    self.tickers = tickers_response
    self.ticker_watchers = ticker_watchers_response

  def get_client():
    return finnhub_client

  # def get_price(self):
  #   # if current price is in tickrs (must be auto-updating at this point)
  #   print('calling price')
  #   # return soupify(self.symbol)
  #   return (self.symbol)
  #   # return parse_finance_page(self.symbol)

  def get_price_from_db(self):
    try:
      ticker = get_object_or_404(Ticker, symbol=self.symbol)
      return ticker['price']
    except:
      return self.get_quote_from_yahoo()

  def yahoo_get_summary(self):
    return self.yahoo_financials.get_summary_data()

  # GET Single FREE_REALTIME YAHOOFINANCES PYPI
  def get_quote_from_yahoo(self):
    # yahoo_financials = YahooFinancials(self.symbol)
    data = self.yahoo_financials.get_stock_price_data(reformat=False)

    formatted_price = ''
    try:
      formatted_price = data[self.symbol]['regularMarketPrice']['fmt']
    except:
      formatted_price = '0'

    return formatted_price


  # GET Multiple FREE_REALTIME YAHOOFINANCES PYPI
  def get_quotes_from_yahoo(self):
    if len(self.symbols) < 1:
      all_ticker_watchers = TickerWatcher.objects.values_list('ticker__symbol', flat=True).distinct()

      self.symbols = all_ticker_watchers

    yahoo_financials = YahooFinancials(self.symbols)

    data = yahoo_financials.get_stock_price_data(reformat=True)

    if data:
      self.update_price_list(yahoo_data=data)
    else:
      print('No data returned from yahoo')

    return data

  def update_price_list(self, yahoo_data):
    ready = False
    price = 0

    for count, symbol in enumerate(yahoo_data):
      try:
        ticker_data = yahoo_data[symbol]
        if ticker_data['regularMarketPrice']:
          price = ticker_data['regularMarketPrice']
          ticker = Ticker.objects.get(symbol=symbol)
          print(f'Symbol: {symbol}, Price: {price}')
          ticker.price = price
          ticker.save()
      except:
        print(f'Error updating prices for {symbol}')

      if count == len(yahoo_data) - 1:
        ready = True

    if ready:
      self.ticker_watchers = TickerWatcher.objects.all()

      self.send_price_alert()

  # Limited by API
  def get_quote_from_finnhub(self):
    return finnhub_client.quote(self.symbol)

  def on_message(self, ws, message):
    message = json.loads(message)
    data = message['data']
    type = message['type']
    trade_data = []
    if type == 'trade':
      for trade in data:
        trade_condition = trade['c']
        trade_symbol = trade['s']
        trade_price = trade['p']
        # 1 == Regular trade
        #  All conditions: https://docs.google.com/spreadsheets/d/1PUxiSWPHSODbaTaoL2Vef6DgU-yFtlRGZf19oBb9Hp0/edit#gid=0
        if '1' in trade_condition:
          trade_data.append({
            'symbol': trade_symbol,
            'price': trade_price
           })

    # Get highest price
    prices = [x['price'] for x in trade_data]

    highest_trade_price = max(prices)

    print(type)
    print(highest_trade_price)
    try:
      ticker = Ticker.objects.get(symbol=trade_symbol)
      ticker.price = trade_price
      ticker.save()
    except:
      print('Error updating price')

  def on_error(self, ws, error):
    print(error)

  def on_close(self, ws):
    print("### closed ###")

  def on_open(self, ws):
    print('{"type":"subscribe","symbol":' + f'"{self.symbol}"' + '}')
    ws.send('{"type":"subscribe","symbol":' + f'"{self.symbol}"' + '}')

  def subscribe(self):
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://ws.finnhub.io?token={}".format(FINNHUB_KEY),
                              on_message = self.on_message,
                              on_error = self.on_error,
                              on_close = self.on_close)
    ws.on_open = self.on_open
    ws.run_forever()

  def send_price_alert(self):
    self.ticker_watchers = TickerWatcher.objects.all()
    watcher_list = {}

    for ticker_watcher in self.ticker_watchers:
      ticker = ticker_watcher.ticker
      if (ticker.price < ticker_watcher.min_price) or  (ticker.price > ticker_watcher.max_price):
        watcher_list[ticker.symbol] = {
          'symbol': ticker.symbol,
          'price': ticker.price,
          'min_price': ticker_watcher.min_price,
          'max_price': ticker_watcher.max_price
        }

    message = ''

    for symbol in watcher_list:
      tick = watcher_list[symbol]
      message += f'''
        ---------------------

        --------------
        Price Alert!!!
        --------------
        {tick['symbol']} - (MIN: {tick['min_price']} - MAX: {tick['max_price']})
        Current Price {tick['price']}'''

    if len(message) > 0:
      twilio.send_message_to_admin(message)
    return watcher_list

  # def update_price_in_ticks(self):
  #   f = open('/data/ticks.py', 'w+')

  def get_candles(self):
    # r = requests.get(f'https://finnhub.io/api/v1/stock/candle?symbol=AAPL&resolution=1&from=1615298999&to=1615302599&token={FINN}')
    # print(r.json())
    # Stock candles
    res = finnhub_client.stock_candles('AAPL', 'D', 1590988249, 1591852249)
    print(res)

    #Convert to Pandas Dataframe
    import pandas as pd
    print(pd.DataFrame(res))

  def get_bars(self):
    d30_days_ago = (datetime.now() - timedelta(30)).strftime('%Y-%m-%d')
    print(d30_days_ago)
    url = f'https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{d30_days_ago}?unadjusted=true'

    response = requests.get(url=url, headers=finnhub_headers)
    print(response.text)

  def iex_get_historical_data(self):
    start = datetime(2017, 1, 1)
    end = datetime(2019, 8, 1)
    df = get_historical_data("DIS", start, end, output_format='pandas')
    print(df)

  # def purchase_stock():

# def live_price_update(symbol):
#   return finnhub_client.last_bid_ask(symbol)py
# class LivePriceUpdate():
#   def __init__(self, symbol = '', symbolList = []):
#     self.symbol = symbol
#     self.symbolList = symbolList

#   def last_bid(symbol):
#     return finnhub_client.last_bid_ask(symbol)

#   def on_message(ws, message):
#     print(message)

#   def on_error(ws, error):
#       print(error)

#   def on_close(ws):
#       print("### closed ###")

#   def on_open(ws):
#       ws.send('{"type":"subscribe","symbol":"AAPL"}')
#       ws.send('{"type":"subscribe","symbol":"AMZN"}')
#       ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')
#       ws.send('{"type":"subscribe","symbol":"IC MARKETS:1"}')

#   if __name__ == "__main__":
#       websocket.enableTrace(True)
#       ws = websocket.WebSocketApp("wss://ws.finnhub.io?token={}".format(key),
#                                 on_message = on_message,
#                                 on_error = on_error,
#                                 on_close = on_close)
#       ws.on_open = on_open
#       ws.run_forever()


# # Register new webhook for earnings
# r = requests.post('https://finnhub.io/api/v1/webhook/add?token={}'.format(key),
# json={'event': 'earnings', 'symbol': 'AAPL'})
# res = r.json()
# print(res)

# webhook_id = res['id']
# # List webhook
# r = requests.get('https://finnhub.io/api/v1/webhook/list?token={}'.format(key))
# res = r.json()
# print(res)

# #Delete webhook
# r = requests.post('https://finnhub.io/api/v1/webhook/delete?token={}'.format(key),
# json={'id': webhook_id})
# res = r.json()
# print(res)
