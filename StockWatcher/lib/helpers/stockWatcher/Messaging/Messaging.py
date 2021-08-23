# MESSAGING


from StockWatcher.lib.helpers.stockWatcher.Messaging.twilio_notifications.middleware import MessageClient, load_twilio_config


class TwilioMessenger():
  def __init__(self):
    load_twilio_config()

  def send_message_to_admin(self, body):
    client = MessageClient()
    admin = client.administrators[0]['phone_number']

    client.send_message(body, admin)


