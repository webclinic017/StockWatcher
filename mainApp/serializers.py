from mainApp.models import Ticker, TickerWatcher
from django.contrib.auth.models import User, Group
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]

class TickerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ticker
        fields = [
            "symbol",
            "name",
            "price",
            "created_at",
            "updated_at",
        ]

class TickerWatcherSerializer(serializers.HyperlinkedModelSerializer):
    watcher = UserSerializer(many=False, read_only=True)
    ticker = TickerSerializer(many=False, read_only=True)

    class Meta:
        model = TickerWatcher
        fields = [
            "watcher",
            "ticker",
            "min_price",
            "max_price",
            "created_at",
            "updated_at",
        ]
