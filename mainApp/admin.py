from django.contrib import admin

# Register your models here.
from .models import Ticker, TickerWatcher

admin.site.register(Ticker)
admin.site.register(TickerWatcher)