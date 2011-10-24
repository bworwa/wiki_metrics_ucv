#Native
from httplib import HTTPConnection
from urlparse import urlparse

class ResponseCodeError(Exception):

	response_code = 0

	def __init__(self, response_code):

		self.response_code = response_code

	def __str__(self):

		return repr(self.response_code)

class Request:

	"""Request types constants"""

	HEAD = "HEAD"
	GET = "GET"

	"""Class variables"""

	current_headers = {}

	current_response_code = 0

	current_xhtml = None

	def __init__(self):

		#TODO

		pass

	def __del__(self):

		#TODO

		pass

	def make(self, request_type, url, user_agent):

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
			request_type,
			path + query_string,
			None,
			{ "User-Agent" : user_agent }
		)

		response = connection.getresponse()

		self.current_response_code = response.status

		for header in response.getheaders():

			self.current_headers[header[0]] = header[1]

		self.verify_response_code()

		if request_type is self.GET:

			current_charset = self.current_headers["content-type"].split(";")[1].replace("charset=", "").strip().upper()

			if current_charset is "UTF-8":

				self.current_xhtml = response.read()

			else:

				self.current_xhtml = unicode(response.read().decode(current_charset)).encode("UTF-8")

		connection.close()

	def cleanup(self):

		self.current_response_code = 0

		self.current_headers = {}

		self.current_xhtml = None

	def verify_response_code(self):

		#From http://docs.python.org/howto/urllib2.html#error-codes
		if self.current_response_code > 299 and self.current_response_code < 600:

			raise ResponseCodeError(self.current_response_code)
