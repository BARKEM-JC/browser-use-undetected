import os
import random


class PROXY:
	"""
	Returns a Camoufox-compatible proxy dictionary upon instantiation.
	"""

	def __new__(cls, host: str = None, port: str = None, username: str = '', password: str = '',
	            country_code: str = None, city: str = None, session_time: int = None):
		# Create the instance temporarily
		self = super().__new__(cls)

		# Collect proxy parameters
		self.host = host or os.getenv('PROXY_HOST', '').strip()
		self.port = port or os.getenv('PROXY_PORT', '').strip()
		self.username = username or os.getenv('PROXY_USERNAME', '').strip()
		self.password = password or os.getenv('PROXY_PASSWORD', '').strip()
		self.country_code = country_code
		self.city = city
		self.session_time = session_time

		if not self.host or not self.port:
			raise ValueError('Host and port must be provided as arguments or environment variables.')

		if (self.username and not self.password) or (self.password and not self.username):
			raise ValueError('Both username and password must be provided, or neither.')

		# Return proxy dictionary directly
		return self._camoufox_proxy()

	def _oxylabs_proxy_username(self) -> str:
		username = "customer-barkem_fINiF"
		if self.country_code:
			username += f"-cc-{self.country_code}"
			if self.city:
				username += f"-city-{self.city}"
		if self.session_time:
			session_id = random.randint(1000000000, 9999999999)
			username += f"-sessid-{session_id}-sesstime-{self.session_time}"
		return username

	def _camoufox_proxy(self) -> dict:
		if "oxylabs.io" in self.host:
			proxy_username = self._oxylabs_proxy_username()
		else:
			proxy_username = self.username

		return {
			'server': f'http://{self.host}:{self.port}',
			'username': proxy_username,
			'password': self.password
		}