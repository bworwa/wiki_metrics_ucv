#Native
from httplib import HTTPConnection
from urlparse import urlparse

class ResponseCodeError(Exception):

	response_code = 0

	error_type = None

	def __init__(self, response_code, error_type):

		self.response_code = response_code

		self.error_type = error_type

	def __str__(self):

		return repr([self.response_code, self.error_type])

class Request:

	current_headers = {}

	current_response_code = 0

	def __init__(self):

		#TODO

		pass

	def __del__(self):

		#TODO

		pass

	def head(self, url, user_agent):

		self.cleanup()

		parsed_url = urlparse(url)

		host = parsed_url[1]

		path = parsed_url[2]

		query_string = parsed_url[4]

		if query_string:
			query_string = "?" + query_string

		#TODO: check params [3]

		connection = HTTPConnection(host)

		connection.request(
			"HEAD",
			path + query_string,
			None,
			{ "User-Agent" : user_agent }
		)

		response = connection.getresponse()

		connection.close()

		self.current_response_code = response.status

		for header in response.getheaders():

			self.current_headers[header[0]] = header[1]

		self.verify_response_code()

	def cleanup(self):

		self.current_response_code = 0

		self.current_headers = {}

	def verify_response_code(self):

		#From http://docs.python.org/howto/urllib2.html#error-codes
		if self.current_response_code > 499 and self.current_response_code < 600:

			raise ResponseCodeError(self.current_response_code, "server")

		elif self.current_response_code > 399 and self.current_response_code < 500:

			raise ResponseCodeError(self.current_response_code, "client")

		elif self.current_response_code > 299 and self.current_response_code < 400:

			raise ResponseCodeError(self.current_response_code, "redirection")
