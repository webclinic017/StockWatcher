import datetime
from dataclasses import dataclass

@dataclass
class Item:
  name: str
  price: int

  def __init__(self, name, price):
    self.name = name
    self.price = price

