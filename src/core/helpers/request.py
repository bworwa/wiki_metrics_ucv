
"""Core libraries, do not change"""

# Native
from httplib import HTTPConnection, HTTPException
from urlparse import urlparse
from robotparser import RobotFileParser
from socket import gaierror, timeout
from time import sleep

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

	XML_MIME_TYPES = [
		"text/html",
		"text/xml",
		"application/xhtml+xml",
		"application/atom+xml",
		"application/xslt+xml",
		"application/mathml+xml",
		"application/xml",
		"application/rss+xml",
		"image/svg+xml"
	]

	TIDY_OPTIONS = {
		"output_xhtml" : True,
		"add_xml_decl" : True,
		"bare" : True,
		"drop_empty_paras" : True,
		"hide_comments" : True,
		"join_classes" : True
	}

	current_headers = {}

	current_response_code = 0

	current_content = "<_/>"

	current_content_type = None

	current_charset = None

	crawl_delay = 1

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

		self.current_content = "<_/>"

		self.current_content_type = None

		self.current_charset = None

		self.crawl_delay = 1

	def knock(self, user_agent, url, override, retries = 0, debug_force_status = None):

		"""
		Makes a request for '/robots.txt' and returns True if 'user_agent' can fetch 'url'. Returns False otherwise
		If we get a HTTP response code other than '200' or any request error occurs, this function will return True
		If we get a gaierror (DNS lookup error), this function will return False as everything else is doomed to fail

		If 'override' is True, this function will automatically return True. Default value for override is False
		"""

		if override:

			return True

		host = urlparse(url)[1]

		robot = RobotFileParser()

		clearance = False

		if retries > 0:

			sleep(self.crawl_delay)

		try:

			# We try to get the resource /robots.txt

			connection = HTTPConnection(host, 80)

			connection.request(
				self.GET,
				"/robots.txt",
				None,
				{ "User-Agent" : user_agent }
			)

			response = connection.getresponse()

			robot_lines = response.read().splitlines()

			connection.close()

			if debug_force_status:

				response.status = debug_force_status

			if response.status == 200 and filter(None, robot_lines) != []:

				# If everthing went well, we feed the content of the resource to the parser

				robot.parse(robot_lines)

				# And resolve if we have clearance to fetch the url

				clearance = robot.can_fetch(user_agent, url)

				# We try to get the Crawl-delay directive, if it exists

				try:

					self.crawl_delay =  int(
						"".join(list(
							directive for directive in robot_lines if directive.lower().startswith("crawl-delay")
						)).split(":")[1]
					)

				except IndexError:

					# If no 'Crawl-delay' is specified, we leave it at 1 second

					pass

			elif response.status in [408, 500, 503]:

				if retries < 3:

					try:

						sleep(self.current_headers["retry-after"] - self.crawl_delay)

					except KeyError:

						pass

					except TypeError:

						pass

					clearance = self.knock(user_agent, url, False, retries + 1)

				else:

					clearance = True

			else:

				clearance = True			

			if retries < 1:

				sleep(self.crawl_delay)

			return clearance

		except HTTPException:

			# A request error occurred. We retry the request, if it fails we just ignore /robots.txt and proceed

			if retries < 3:

				return self.knock(user_agent, url, False, retries + 1)

			else:

				return True

		except timeout:

			# Request timed out. We retry the request, if it fails we just ignore /robots.txt and proceed

			if retries < 3:

				return self.knock(user_agent, url, False, retries + 1)

			else:

				return True

	def make(self, url, request_type, user_agent, desired_charset, debug_force_status = None):

		"""
		Makes a request for the resource identified by 'url' of the type 'request_type' (supported types are 'HEAD' and 'GET')
		using the user agent 'user_agent'

		If the resource's content is (X)HTML/XML, it'll then be encoded to the desired charset ('desired_charset')
		(this only in case that the resource's current charset is different from the desired_charset)

		Note: The (X)HTML/XML obtained will be tidied so 'self.current_content' might not be an exact copy of the resource's content
		"""

		# We clean up all our variables before making another request

		self.clean_up()

		# Then parse the URL and construct the 'path + query' string
		# We discard the fragments as they are of no use (at least for synchronous requests)

		parsed_url = urlparse(url, None, False)

		scheme = parsed_url[0]

		host = parsed_url[1]

		path = parsed_url[2]

		path_parameters = parsed_url[3]

		query_string = parsed_url[4]

		if path_parameters:

			path_parameters = ";" + path_parameters

		if query_string:

			query_string = "?" + query_string
			
		# We create our HTTP connection instance (no request sent yet)

		connection = HTTPConnection(host, 80, False, 25)

		# And make the request for the 'path + query' specified resource (request sent)

		connection.request(
			request_type,
			"/" + path + path_parameters + query_string,
			None,
			{ "User-Agent" : user_agent }
		)

		# We get the current response from the server (response code, headers, etc.)

		response = connection.getresponse()

		connection.close()

		if debug_force_status:

			self.current_response_code = debug_force_status

		else:

			self.current_response_code = response.status

		# We make our own dictionary of headers as it will be more easy and natural to consult

		for header in response.getheaders():

			self.current_headers[header[0]] = header[1]

		# We verify the response code. If it wasn't a successful request (2xx) execution ends here

		self.verify_response_code()

		# At this point we have made a successful request and start processing the resource's content (in case of a GET request)
		# For HEAD requests execution ends here

		try:

			# We try to get the 'content-type' header in order to know the MIME-type of the resource

			content_type_header = self.current_headers["content-type"].lower().split(";")

			content_type_header = list(
				fragment.strip() for fragment in content_type_header
			)

			# We get the content type

			self.current_content_type = content_type_header[0]

		except KeyError:

			# [Low] TODO

			pass

		if request_type == self.GET and self.current_content_type in self.XML_MIME_TYPES:

			# We get the content of the resource and strip it

			self.current_content = response.read().strip()

			try:

				# We then try to get the resource's charset from the 'content-type' header	

				self.current_charset = content_type_header[1]

				for substring in ["charset=", "-"]:

					self.current_charset = self.current_charset.replace(substring, "")

				if self.current_charset == "iso88591":

					self.current_charset = "latin1"

			except IndexError:

				# There was no 'charset' defined in the 'content-type' header, we default to the specified
				# 'desired_charset'. This could, and probably will, cause problems

					self.current_charset = desired_charset

			if not self.current_charset == desired_charset:

				self.current_content = unicode(
					self.current_content.decode(self.current_charset, "replace")
				).encode(desired_charset, "ignore")

			self.TIDY_OPTIONS["char_encoding"] = desired_charset

			# Finally we tidy up the (X)HTML/XML and it's ready to be parsed

			self.current_content = parseString(self.current_content, **self.TIDY_OPTIONS).__str__()		

		# We close the connection and end the execution

		sleep(self.crawl_delay)

	def verify_response_code(self):

		# According to http://docs.python.org/howto/urllib2.html#error-codes

		if self.current_response_code > 299 and self.current_response_code < 600:

			raise ResponseCodeError(self.current_response_code)
