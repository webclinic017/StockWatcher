import json
import re
from django.db.models.query_utils import Q
from StockWatcher.lib.helpers.stockWatcher.Autocomplete import TickerAutocomplete
from StockWatcher.lib.helpers.stockWatcher.LiveUpdate import LivePriceUpdate
from StockWatcher.lib.helpers.stockWatcher.Messaging.twilio_notifications.middleware import MessageClient
from django.http.response import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.views.generic.base import View
from django.views.generic.edit import FormView
from django.urls import reverse
from .forms import SendMessageForm, TickrAutocomplete, WatchStockForm
from .models import Ticker, TickerWatcher
from django.shortcuts import get_object_or_404, render
# class VoteForCatsView(FormView):
#   template_name = './index.html'
#   form_class  = VoteForCatsView

#   def form_valid(self, form):
#       votes = form.cleaned_data.get('votes')
#       vote_for_cats.delay(votes)
#       messages.success(self.request, 'We are proccessing your request. Refresh the page after a few moments.')

#       return redirect('/polls')

class TickrAutocomplete(FormView):
  template_name = './index.html'
  form_class = TickrAutocomplete
  ticks = []

  def set_ticks(self):
    ticker_watchers = TickerWatcher.objects.filter(watcher__id=self.request.user.id).order_by('updated_at')

    ticks = []
    for tick in ticker_watchers.all():
      ticks.append({
        'id': tick.id,
        'ticker_id': tick.ticker.id,
        'symbol': tick.ticker.symbol,
        'current_price': tick.ticker.price,
        'min_price': tick.min_price,
        'max_price': tick.max_price,
        'last_updated': tick.ticker.updated_at
      })

      self.ticks  = ticks


  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    self.set_ticks()
    context['ticker_watchers'] = self.ticks

    return context

  def form_valid(self, form):
    query = form.cleaned_data.get('query')

    autocomplete = TickerAutocomplete(query=query)
    results = autocomplete.get_results(query)
    symbols = autocomplete.get_symbols(query)
    self.set_ticks()

    context = { 'data': results, 'ticker_watchers': self.ticks }

    return JsonResponse(context)

class LivePriceUpdateView(View):
  def get(self, request):
    symbol = request.GET['symbol']

    if self.request.user.is_superuser:
      live_update = LivePriceUpdate(symbol)
      price = live_update.get_quote_from_yahoo()
      # live_update.subscribe()
      live_update.get_bars()

      return JsonResponse({ 'price': price })
    else:
      return JsonResponse({ 'error': 'Please sign in as a superuser.' })



class WatchStockView(View):

  def get(self, request, symbol):
    symbol = self.kwargs['symbol']
    price = request.GET['price']

    request.session['symbol'] = symbol
    request.session['price'] = price

    if self.request.user.is_superuser:
      return HttpResponseRedirect(reverse('mainApp:watch_stock', kwargs={'symbol': symbol, 'price': price}))
    else:
      return render(self.request, template_name="./watch_stock.html", context={'error': 'Please sign in to save a new ticker' })

class WatchStockFormView(FormView):
  template_name = "./watch_stock.html"
  form_class = WatchStockForm

  def get_context_data(self, **kwargs):
    symbol = self.kwargs['symbol']
    price = self.kwargs['price']

    context = super().get_context_data(**kwargs)
    context["symbol"] = symbol

    ticker_watchers = TickerWatcher.objects.filter(watcher__id=self.request.user.id).order_by('updated_at')

    ticks = []
    for tick in ticker_watchers.all():
      ticks.append({
        'id': tick.id,
        'ticker_id': tick.ticker.id,
        'symbol': tick.ticker.symbol,
        'current_price': tick.ticker.price,
        'min_price': tick.min_price,
        'max_price': tick.max_price,
        'last_updated': tick.ticker.updated_at
      })

    context['ticker_watchers'] = ticks

    return context

  def form_valid(self, form):
    request_symbol = self.kwargs['symbol']
    updated_price = self.kwargs['price']
    min_price = form.cleaned_data.get('min_price')
    max_price = form.cleaned_data.get('max_price')
    print(updated_price)

    # Get ticker or create ticker
    # ticker = get_object_or_404(Ticker, symbol=request_symbol)
    # print(updated_price, request_symbol)
    # autocomplete = TickerAutocomplete(request_symbol)
    # live_update = LivePriceUpdate(request_symbol)
    # ticker_info = autocomplete.get_name_from_symbol()
    # ticker_updated_price = live_update.get_quote_from_yahoo()


    # GET/CREATE Ticker
    # ticker, new_ticker_created = Ticker.objects.get_object_or_404(
    #     symbol = request_symbol
    #   )
    current_ticker = {}

    try:
      ticker = get_object_or_404(Ticker, symbol=request_symbol)
      ticker.price = updated_price
      ticker.save()
      current_ticker = ticker
    except:
      print('No Ticker found, creating new Ticker')

      try:
        ticker = Ticker(symbol=request_symbol, price=updated_price)
        ticker.save()
        current_ticker = ticker
      except:
        print('Problem creating new ticker')
        return render(self.request, template_name=self.template_name, context={'error': 'Problem creating new ticker.' })

    try:
      # GET/CREATE TickerWatcher
      new_ticker_watcher = TickerWatcher(
        watcher = self.request.user,
        ticker = current_ticker,
        min_price=min_price,
        max_price=max_price
      )

      new_ticker_watcher.save()

      self.request.session['success'] = True
      print('new watcher created')
    except:
      self.request.session['success'] = False
      print('new watcher failed')
      return render(self.request, template_name=self.template_name, context={'symbol': request_symbol, 'price': updated_price, 'error': 'New watcher failed to save' })

    return HttpResponseRedirect(reverse(
      "mainApp:watch_stock", kwargs={'symbol': request_symbol, 'price': updated_price }))

  def form_invalid(self, form):
    self.request.session['success'] = False
    print('invalid form submission')
    return HttpResponseRedirect(self.request.path)


class SendMessageFormView(FormView):
  '''For Testing Only'''
  template_name = "./send_message.html"
  form_class = SendMessageForm

  # def get_context_data(self, **kwargs):
  #   live_update = LivePriceUpdate()
  #   watcher_list = live_update.send_price_alert()
  #   return { 'watcher_list': watcher_list }

  def form_valid(self, form):
    to = form.cleaned_data.get('to')
    message = form.cleaned_data.get('message')

    client = MessageClient()
    client.send_message(message, to)
    # send('test')
    return HttpResponseRedirect(self.request.path)

def TestView(request):


  if request.method == 'GET':
    try:
      tickers = ['IDEX', 'BB', 'CLNE', 'AMC', 'CCL', 'JMIA', 'TRCH']
      live_update = LivePriceUpdate(tickers)
      data = live_update.get_quotes_from_yahoo()
      print(data)
      return HttpResponse(content=data)


    except:
      return HttpResponseBadRequest(content='Error')
