import json

import requests
import re
import csv
import os

FINNHUB_KEY = os.environ['FINNHUB_KEY']
class TickerAutocomplete():
  tickers = []

  def __init__(self, query = '', autocomplete_results = [], symbols = []):
    self.query = query
    self.autocomplete_results = autocomplete_results
    self.symbols = symbols

    with open('stockWatcher/lib/data/ticks.json', 'r') as f:
      self.tickers = json.load(f)

  # def tickr_autocomplete(self, query):
  #   results = []
  #   symbols = []

  #   print(query)
  #   for symbol in range(len(self.tickers)):
  #     print(symbol)
  #     for key in self.tickers[symbol]:
  #       if key == 'symbol':
  #         # if query.upper() in tickrs[symbol][key]:
  #         # if re.search('^{}'.format(query.upper()), self.tickers[symbol][key]):
  #         print(f'KEy: {key}, Query: {query}')
  #         if query.upper() in self.tickers['symbol'][key]:
  #           results.append(self.tickers[symbol])
  #           symbols.append(self.tickers[symbol][key])

  #   self.results = results
  #   self.symbols = symbols
  #   return results

  def autocomplete_search(self, query, include_name_in_search):
    if not query or len(query) < 1:
      return self.autocomplete_results

    suggestions = []
    query = query.upper()

    for ticker in self.tickers:
      ticker_symbol = ticker['symbol']
      ticker_name = ticker['name']
      full_name =  f'{ticker_symbol} - {ticker_name}'

      # if query.upper() in ticker['symbol'] or (include_name_in_search == 'true' and query in ticker['name']):
      if re.match(r'^' + query.upper(), ticker['symbol']) or (include_name_in_search == 'true' and re.match(r'^' + query.upper(), ticker['name'])):
        if full_name not in suggestions:
          suggestions.append(full_name)

    def smallest_symbol_len(ticker_string):
      return len(ticker_string.split('-')[0].replace(' ', ''))

    print(suggestions)
    suggestions.sort(key=smallest_symbol_len)

    self.autocomplete_results = suggestions
    print(suggestions)
    return suggestions

  # def get_results(self, query):
  #   if query:
  #     results = self.tickr_autocomplete(query)
  #     return results
  #   else:
  #     return self.autocomplete_results

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

    matching_ticker = filter(lambda ticker: ticker['symbol'] == self.query, self.tickers)

    return next(matching_ticker)


# a = TickerAutocomplete().refresh_symbols()