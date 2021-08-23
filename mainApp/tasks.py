from datetime import datetime, timedelta
from time import time
from StockWatcher.lib.helpers.stockWatcher.LiveUpdate import LivePriceUpdate
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from .celery import app
from django.apps import apps
import requests

logger = get_task_logger('stockWatcher')

try:
  # Models
  TICKER_WATCHER = apps.get_model(app_label="mainApp", model_name="TickerWatcher")
  TICKERS = apps.get_model(app_label="mainApp", model_name="TickerWatcher")

  # Ticker Symbols
  ticker_symbols = TICKER_WATCHER.objects.values_list('ticker__symbol').distinct()
  all_ticker_symbols = []

  for ticker in ticker_symbols.all():
    if ticker[0] not in all_ticker_symbols:
      all_ticker_symbols.append(ticker[0])

  # Live Update
  live_update = LivePriceUpdate(symbols=all_ticker_symbols)
except:
  logger.error(msg='failed to load models')

# STOCK UPDATES
@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
  sender.add_periodic_task(
    # PRODUCTION
    crontab(day_of_week='1-5', hour='09-16', minute='*/30'), # not working and invalid for unknown timezone
    # DEVELOPMENT
    # 1800,
    # 30,
    refresh_symbols.s(),
    name='stocks refreshed every 30 minutes'
  )

#  RUN IN PROD ONLY

# Refresh Stocks
@app.task
def refresh_symbols():
  """Refresh the Tickers price with the current live price"""
  # print(f'Keeping heroku alive')
  # logger.info(f'Keeping Heroku alive')
  # response = requests.get('/')
  # logger.debug(response)
  # print(response)
  logger.info(f'Getting price updates for these tickers: {all_ticker_symbols}')
  live_update.get_quotes_from_yahoo()
  # may need for big list of ticker_watchers (time to load can take unknown time)
  # send_message_if_ticker_watcher_is_out_of_range.delay()

# @app.task
# def send_message_if_ticker_watcher_is_out_of_range():
#   logger.info('Sending admin message with stock alert')
#   live_update.send_price_alert()


# LOGGER FOR CRONTRAB
# @app.task
# def log_contrab():
#   logs = crontab(day_of_week='mon-fri', hour='15,16,17,18,19,20, 21, 22, 23')
#   if logs:
#     logger.info(f'{logs.__repr__}')
#   else:
#     logger.info('no logs')
