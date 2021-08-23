"""aPollingApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
# from polls.views import IndexView
from . import views

app_name = 'mainApp'

urlpatterns = [
    # path('', IndexView.as_view(), name="index"),
    # path("", views.VoteForCatsView.as_view(), name="home"),
    # path("", views.TickrAutocomplete.as_view(), name="search"),
    path("live_update/", views.LivePriceUpdateView.as_view(), name="live_update"),
    path('watch/<symbol>/', views.WatchStockView.as_view(), name="watch"),
    path('watch_stock/<symbol>/<price>', views.WatchStockFormView.as_view(), name="watch_stock"),
    path('send_message/', views.SendMessageFormView.as_view(), name="send_message"),
    path('test/', views.TestView, name="test"),
]
