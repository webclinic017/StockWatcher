from django import forms
from django.core.validators import MinValueValidator

class TickrAutocomplete(forms.Form):
  query = forms.CharField(min_length=2, max_length=6)


class WatchStockForm(forms.Form):
  min_price = forms.DecimalField(
    validators=[
      MinValueValidator(0)
    ]
  )
  max_price = forms.DecimalField(
    validators=[
      MinValueValidator(0)
    ]
  )

class SendMessageForm(forms.Form):
  to = forms.CharField(empty_value='6476404714')
  message = forms.CharField(widget=forms.Textarea)
