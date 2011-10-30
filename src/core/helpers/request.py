
"""Core libraries, do not change"""

# Native
from httplib import HTTPConnection
from urlparse import urlparse

# External
from tidy import parseString

class ResponseCodeError(Exception):

	"""Custom exception to be raised when a request response code is greater than 2xx"""

	response_code = 0

	def __init__(self, response_code):

		self.response_code = response_code

	def __str__(self):

		return repr(self.response_code)

class Request:

	HEAD = "HEAD"
	GET = "GET"

	current_headers = {}

	current_response_code = 0

	current_content = "<empty></empty>"

	current_content_type = None

	current_charset = None

	def __init__(self):

		# [Low] TODO

		pass

	def __del__(self):

		# [Low] TODO

		pass

	def clean_up(self):

		"""Restarts all the class variables"""

		self.current_headers = {}

		self.current_response_code = 0

		current_content = "<empty></empty>"

		self.current_content_type = None

		self.current_charset = None

	def make(self, url, request_type, user_agent = None, charset = None, xml_mime_types = []):

		"""
		Makes a request to 'url' of the type 'request_type' (Supported types are 'HEAD' and 'GET')

		Default user agent is None (some hosts do require a user agent in their requests)
		Default charset is None as it isn't required for HEAD requests. However, it is STRICTLY necessary for GET requests
		Default xml_mime_types is [] as it isn't required for HEAD requests. However, it is STRICTLY necessary for GET requests
		"""

		# We clean up all our variables before making another request

		self.clean_up()

		# Then parse the URL and construct the 'path + query' string
		# We discard the fragments as they are of no use (at least for synchronous requests)

		parsed_url = urlparse(url, None, False)

		host = parsed_url[1]

		path = parsed_url[2]

		path_parameters = parsed_url[3]

		query_string = parsed_url[4]

		if path_parameters:

			path_parameters = ";" + path_parameters

		if query_string:
			query_string = "?" + query_string
			
		# We create our HTTP connection instance (no request sent yet)

		connection = HTTPConnection(host, 80, False, 30)

		# And make the request for the 'path + query' specified resource (request sent)

		connection.request(
			request_type,
			path + path_parameters + query_string,
			None,
			{ "User-Agent" : user_agent }
		)

		# We get the current (last) response from the server (response code, headers, etc.)

		response = connection.getresponse()

		self.current_response_code = response.status

		# We make our own dictionary of headers as it will be more easy and natural to consult

		for header in response.getheaders():

			self.current_headers[header[0]] = header[1]

		# We verify the response code. If it wasn't a successful request (2xx) execution ends here

		self.verify_response_code(connection)

		# At this point we have made a successful request and start processing the resource's content (in case of a GET request)
		# For HEAD requests execution ends here

		try:

			# We try to get the 'content-type' header in order to know the MIME-type of the resource

			content_type_header = self.current_headers["content-type"].split(";")

			content_type_header = list(
				fragment.strip() for fragment in content_type_header
			)

			# We get the content type

			self.current_content_type = content_type_header[0].lower()

		except KeyError:

			# [Medium] TODO

			pass

		if request_type == self.GET and self.current_content_type in xml_mime_types:

			# We get the content of the resource and strip it

			self.current_content = response.read().strip()

			# We set the Tidy options

			tidy_options = {
				"output_xhtml" : True,
				"add_xml_decl" : True,
				"bare" : True,
				"drop_empty_paras" : True,
				"hide_comments" : True,
				"join_classes" : True
			}

			try:

				# We then try to get the resource's charset from the 'content-type' header	

				self.current_charset = content_type_header[1]

				for substring in ["charset=", "-"]:

					self.current_charset = self.current_charset.replace(substring, "")

				self.current_charset = self.current_charset.upper()

			except IndexError:

				# There was no 'charset' defined in the 'content-type' header, we default to the specified 'charset'.
				# This could, and probably will, cause problems

				self.current_charset = charset

				# [Medium] TODO: normalize charsets

			if charset:

				tidy_options["char_encoding"] = charset

				if not self.current_charset == charset:

					# Now we step into marshland and begin the cumbersome task of character encoding

					# [High] TODO: try, try, try...

					self.current_content = unicode(self.current_content.decode(self.current_charset)).encode(charset)

			# Finally we tidy up the XHTML and it's ready to be parsed

			self.current_content = parseString(self.current_content, **tidy_options).__str__()		

		# We close the connection and end the execution

		connection.close()

	def verify_response_code(self, connection):

		# According to http://docs.python.org/howto/urllib2.html#error-codes

		if self.current_response_code > 299 and self.current_response_code < 600:

			connection.close()

			raise ResponseCodeError(self.current_response_code)
