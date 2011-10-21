#Native
from BaseHTTPServer import BaseHTTPRequestHandler
from httplib import HTTPConnection
from urlparse import urlparse

class ResponseCodeError(Exception):

	explanation = None

	def __init__(self, explanation):

		self.explanation = explanation

	def __str__(self):

		return repr(self.explanation)

class Request:

	current_headers = []

	current_response_code = 0

	def __init__(self):

		#TODO

		pass

	def __del__(self):

		#TODO

		pass

	def head(self, url, user_agent):

		parsed_url = urlparse(url)

		host = parsed_url[1]

		path = parsed_url[2]

		query_string = parsed_url[4]

		if query_string:
			query_string = "?" + query_string

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

		self.current_headers = response.getheaders()

		self.verify_response_code()

	def verify_response_code(self):

		#from http://docs.python.org/howto/urllib2.html#error-codes
		if self.current_response_code > 399 and self.current_response_code < 600:

			raise ResponseCodeError(BaseHTTPRequestHandler.responses[self.current_response_code][1])
