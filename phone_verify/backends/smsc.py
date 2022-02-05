from __future__ import absolute_import
from .base import BaseBackend
from phone_verify.models import SMSVerification

import requests
import json
import random

SMSC_LOGIN = "todomaketobe"
SMSC_PASSWORD = "Zapyata1a"

class SmscBackend(BaseBackend):

	def __init__(self, **options):
		super().__init__(**options)

		# Lower case it just to be sure
		options = {key.lower(): value for key, value in options.items()}
		self._key = options.get("key", None)
		self._secret = options.get("secret", None)
		self._from = options.get("from", None)

		# Create a Nexmo Client object
		

	def create_security_code_and_session_token(self, number):
		"""
		Creates a temporary `security_code` and `session_token` inside the DB.
		`security_code` is the code that user would enter to verify their phone_number.
		`session_token` is used to verify if the subsequent call for verification is
		by the same device that initiated a phone number verification in the
		first place.
		:param number: Phone number of recipient
		:return security_code: string of sha security_code
		:return session_token: string of session_token
		"""
		message = ''
		security_code = self.send_sms(number, message)
		session_token = self.generate_session_token(number)

		# Delete old security_code(s) for phone_number if already exists
		SMSVerification.objects.filter(phone_number=number).delete()

		# Default security_code generated of 6 digits
		SMSVerification.objects.create(
			phone_number=number,
			security_code=security_code,
			session_token=session_token,
		)
		print("BD object: " + json.dumps(security_code))
		return security_code, session_token

	def send_verification(self, number, security_code):
		pass

	def send_sms(self, number, message):
		# Implement your service's SMS sending functionality
		# self.client = SMSC()
		number = int(number.replace("+", ""))
		print("Number: " + str(number))
		payload = {
			'login': SMSC_LOGIN,
			'psw': SMSC_PASSWORD,
			'phones': number,
			'mes': 'code',
			'format': 9,
			'fmt': 3,
			'call': 1,
			}
		
		r = requests.get('https://smsc.ru/sys/send.php', params=payload)
		
		print("request: " + r.url)
		print("response: " + str(r.text))
		
		security_code = json.loads(r.text)["code"]

		print("Код: " + security_code)
		return security_code

	# def send_sms(self, number, message):
	# 	# Implement your service's SMS sending functionality
	# 	self.client = SMSC()
	# 	return self.client._smsc_send_cmd(phones=number, call=1)

	def send_bulk_sms(self, numbers, message):
		for number in numbers:
			self.send_sms(number=number, message=message, sender="Woo")