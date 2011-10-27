
"""Core libraries, do not change"""

# Native
from httplib import HTTPConnection
from urlparse import urlparse

# External
from tidy import parseString

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

	def clean_up(self):

		self.current_response_code = 0

		self.current_headers = {}

		self.current_xhtml = None

	def make(self, request_type, url, user_agent, charset = None):

		# We default charset to None because it isn't needed for HEAD requests
		# However it is STRICTLY necessary for GET requests

		self.clean_up()

		parsed_url = urlparse(url)

		host = parsed_url[1]

		path = parsed_url[2]

		query_string = parsed_url[4]

		if query_string:
			query_string = "?" + query_string
			
		#TODO: check params [3]

		connection = HTTPConnection(host, 80, False, 30)

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

		if request_type == self.GET:

			self.current_xhtml = response.read().strip()

			#TODO: try

			current_charset = self.current_headers["content-type"].split(";")[1]

			for substring in ["charset=", "-"]:

				current_charset = current_charset.replace(substring, "")

			current_charset = current_charset.strip().upper()			

			if self.current_xhtml:

				if not current_charset == charset:

					#TODO: try

					self.current_xhtml = unicode(self.current_xhtml.decode(current_charset)).encode(charset)

				tidy_options = {
					"output_xhtml" : True,
					"add_xml_decl" : True,
					"bare" : True,
					"drop_empty_paras" : True,
					"drop_proprietary_attributes" : True,
					"escape_cdata" : True,
					"hide_comments" : True,
					"join_classes" : True,
					"char_encoding" : charset,
					"output_bom" : True
				}

				self.current_xhtml = parseString(self.current_xhtml, **tidy_options).__str__()

		connection.close()

	def verify_response_code(self):

		#From http://docs.python.org/howto/urllib2.html#error-codes

		if self.current_response_code > 299 and self.current_response_code < 600:

			raise ResponseCodeError(self.current_response_code)
