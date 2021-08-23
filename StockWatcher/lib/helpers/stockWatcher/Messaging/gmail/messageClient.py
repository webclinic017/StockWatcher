import asyncio
import re
from email.message import EmailMessage
from typing import Tuple, Union

import aiosmtplib

HOST = "smtp.gmail.com"
import smtplib
carriers = {
	'att':    '@mms.att.net',
	'tmobile':' @tmomail.net',
	'verizon':  '@vtext.com',
	'sprint':   '@page.nextel.com'
}

CARRIER_MAP = {
    "verizon": "vtext.com",
    "tmobile": "tmomail.net",
    "sprint": "messaging.sprintpcs.com",
    "at&t": "txt.att.net",
    "boost": "smsmyboostmobile.com",
    "cricket": "sms.cricketwireless.net",
    "uscellular": "email.uscc.net",
		"rogers": "@pcs.rogers.com"
}

class GmailMessage():

	async def send_txt(
    num: Union[str, int],
		carrier: str,
		email: str,
		pword: str,
		msg: str,
		subj: str
		) -> Tuple[dict, str]:
			to_email = CARRIER_MAP[carrier]

			# build message
			message = EmailMessage()
			message["From"] = email
			message["To"] = f"{num}@{to_email}"
			message["Subject"] = subj
			message.set_content(msg)

			# send
			send_kws = dict(username=email, password=pword, hostname=HOST, port=587, start_tls=True)
			res = await aiosmtplib.send(message, **send_kws)  # type: ignore
			msg = "failed" if not re.search(r"\sOK\s", res[1]) else "succeeded"
			print(msg)
			return res
	def send(self, message):
		print(message)
					# Replace the number with your own, or consider using an argument\dict for multiple people.
		# to_number = '000-000-0000{}'.format(carriers['att'])
		to_number = '+16476404714'
		auth = ('benaimjacob@gmail.com', 'Jb100831792!')

		# Establish a secure session with gmail's outgoing SMTP server using your gmail account
		server =  smtplib.SMTP( "smtp.gmail.com", 465 )
		server.starttls()
		server.login(auth[0], auth[1])

		# Send text message through SMS gateway of destination number
		server.sendmail( auth[0], to_number, message)

	# def test_mail_to_sms():
		# from django.core.mail import send_mail
		# send_mail('','test','',['my_number@mynetwork'])

		# send('test')

# gmail = GmailMessage()

# auth = {
# 	'email':'benaimjacob@gmail.com',
# 	'password':'Jb100831792!'
# }

# coro = gmail.send_txt(
# 	carrier="rogers",
# 	email=auth['email'],
# 	pword=auth['password'],
# 	msg='tets',
# 	subj='test sub'
# 	)
# asyncio.run(coro)


# gmail.send('messge')