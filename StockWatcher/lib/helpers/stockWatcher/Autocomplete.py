import json

import requests
import re
import csv
import os

FINNHUB_KEY = os.environ['FINNHUB_KEY']

tickers = []

with open('stockWatcher/lib/data/ticks.json', 'r') as f:
  tickers = f.read()
class TickerAutocomplete():
  def __init__(self, query = '', results = [], symbols = []):
    self.query = query
    self.results = results
    self.symbols = symbols

  def tickr_autocomplete(self, query):
    results = []
    symbols = []

    for symbol in range(len(tickers)):
      for key in tickers[symbol]:
        if key == 'symbol':
          # if query.upper() in tickrs[symbol][key]:
          if re.search('^{}'.format(query.upper()), tickers[symbol][key]):
            results.append(tickers[symbol])
            symbols.append(tickers[symbol][key])

    self.results = results
    self.symbols = symbols
    return results

  def tickr_autocomplete(self, query):
    matching_ticker = filter(lambda ticker: ticker['symbol'] == query, tickers)

    return next(matching_ticker)

  def get_results(self, query = ''):
    if query:
      self.tickr_autocomplete(query)
      return self.results
    else:
      return self.results

  def get_symbols(self, query = ''):
    if query:
      self.tickr_autocomplete(query)
      return self.symbols
    else:
      return self.symbols

  def refresh_symbols(self):
    r = requests.get('https://finnhub.io/api/v1/stock/symbol?exchange=US&token={}'.format(FINNHUB_KEY))

    data = []
    for i, ticker in enumerate(r.json()):
      tick = {}
      tick['id'] = i
      tick['symbol'] = ticker['symbol']
      tick['name'] = ticker['description']

      data.append(tick)

    f = open('StockWatcher/lib/data/ticks.json', 'w+')
    f.truncate(0)
    f.write(f'{json.dumps(data)}')
    f.close()

    return r.json()

  def get_name_from_symbol(self):

    matching_ticker = filter(lambda ticker: ticker['symbol'] == self.query, tickers)

    return next(matching_ticker)


a = TickerAutocomplete().refresh_symbols()