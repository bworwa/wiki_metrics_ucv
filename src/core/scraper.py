
"""Core libraries, do not change"""

# Native
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from urlparse import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler
from email.utils import parsedate
from time import time, localtime, mktime
from socket import gaierror, timeout
from httplib import HTTPException, NotConnected, InvalidURL, UnknownProtocol, UnknownTransferEncoding, UnimplementedFileMode, IncompleteRead, ImproperConnectionState, BadStatusLine
from os.path import abspath, dirname

# XCraper
from messages import Messages
from helpers.validation import Validation
from helpers.request import Request, ResponseCodeError
from helpers.custom_xpath import Xpath

# External
from xpath import XPathNotImplementedError, XPathParseError, XPathTypeError, XPathUnknownFunctionError, XPathUnknownPrefixError, XPathUnknownVariableError

class Scraper:

	config = {
		"path_to_config" : dirname(dirname(dirname(abspath(__file__)))) + "/config/scraper.xml",
		"xpath_queries" : {},
		"user_agent" : None,
		"supported_charsets" : [
			"utf8",
			"ascii"
		],
		"charset" : None
	}

	messages = Messages()

	validation = Validation()

	request = Request()

	xpath = Xpath()

	def __init__(self):

		"""Constructor"""

		# We try to open the xml configuration file (self.config["path_to_config"]) and parse it
		# WE WILL NOT TIDY IT, it must be a valid XML file

		try:

			dom = minidom.parse(self.config["path_to_config"])

		except IOError:

			# I/O error, e.g: open/read/race conditions, low level stuff; program halted

			self.messages.raise_error(self.messages.XML_CONFIG_IO_ERROR % {
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		except ExpatError:

			# Invalid XML file, program halted

			self.messages.raise_error(self.messages.INVALID_XML_FILE % {
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		# Now that the file is open we try to get the root node ('scraper') from the XML configuration file

		try:

			root = dom.getElementsByTagName("scraper")[0]

		except IndexError:

			# The 'scraper' node is missing, program halted

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "scraper",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		# We try to get the 'general' node from the root node

		try:

			general = root.getElementsByTagName("general")[0]

		except IndexError:

			# The 'general' node is missing, program halted

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "general",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		# We get the 'user_agent' and 'charset' tag from the general node

		user_agent = general.getElementsByTagName("user_agent")

		charset = general.getElementsByTagName("charset")
			
		# We 'poke' the variable user_agent[0] to see if there is a 'user_agent' tag defined in the XML configuration file

		try:

			user_agent[0]

		except IndexError:

			# The tag 'user_agent' is missing, program halted

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "user_agent",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		# We verify that the 'user_agent' tag content exists and is not an empty (whitespace) string

		if not user_agent[0].firstChild or not user_agent[0].firstChild.nodeValue.strip():

			# 'user_agent' tag content doesn't exists (empty) or is an empty string (whitespace), program halted

			self.messages.raise_error(self.messages.EMPTY_XML_TAG_VALUE % {
				"xml_tag_name" : "user_agent",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		self.config["user_agent"] = user_agent[0].firstChild.nodeValue.strip()

		# We 'poke' the variable charset[0] to see if there is a 'charset' tag defined in the XML configuration file

		try:

			charset[0]

		except IndexError:

			# The tag 'charset' is missing, program halted

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "charset",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		# We verify that the 'charset' tag content exists and is not an empty (whitespace) string

		if not charset[0].firstChild or not charset[0].firstChild.nodeValue.strip():

			# 'charset' tag content doesn't exists (empty) or is an empty string (whitespace), program halted

			self.messages.raise_error(self.messages.EMPTY_XML_TAG_VALUE % {
				"xml_tag_name" : "charset",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		self.config["charset"] = charset[0].firstChild.nodeValue.replace("-", "").strip().lower()

		if not self.config["charset"] in self.config["supported_charsets"]:

			# The specified charset is not currently supported

			self.messages.raise_error(self.messages.CHARSET_NOT_SUPPORTED % {
				"charset" : self.config["charset"],
				"supported_charsets" : repr(self.config["supported_charsets"])
			}, self.messages.INTERNAL)

		# We try to get the 'xpath' node from the root node

		try:

			xpath_config = root.getElementsByTagName("xpath")[0]

		except IndexError:

			# 'xpath' node is missing, program halted

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "xpath",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		# We try to get the 'queries' tag from the 'xpath' node

		queries = xpath_config.getElementsByTagName("queries")

		if not queries:

			# 'queries' tag is missing, program halted

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "queries",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		# This is a sandbox we create to test the XPath queries. There's no point in having to do a GET request
		# in order to see if a query is invalid
		#
		# This is a controlled enviroment so there's no need to try:except it

		sandbox = minidom.parseString("<sandbox>test</sandbox>")

		for query in queries:

			# We need to associate every set of queries to one or serveral hosts
			# So we get the 'hosts' attribute, clean it and create a list of hosts for the current 'queries' tag

			query_hosts = query.getAttribute("hosts").strip().lower().split(",")

			query_hosts = filter(None, query_hosts)

			query_hosts = list(
				query_host.lstrip() for query_host in query_hosts
			)

			if not query_hosts:

				# Attribute 'hosts' was not specified (empty) or was empty (whitespace), program halted

				self.messages.raise_error(self.messages.EMPTY_XML_TAG_ATTR % {
					"xml_tag_attr" : "queries['hosts']",
					"path_to_xml" : self.config["path_to_config"]
				}, self.messages.INTERNAL)

			# We get the current set of queries corresponding to the hosts (^)

			xpath_queries = query.getElementsByTagName("query")

			if not xpath_queries:

				# 'query' tag is missing. Every host must have at least one query, program halted

				self.messages.raise_error(self.messages.XML_TAG_MISSING % {
					"xml_tag_name" : "query",
					"path_to_xml" : self.config["path_to_config"]
				}, self.messages.INTERNAL)

			for query_host in query_hosts:

				# We treat every host independently so it will have its own set of queries

				self.config["xpath_queries"][query_host] = []

				for xpath_query in xpath_queries:

					# We need to have a list of used query names to avoid duplicated names

					declared_xpath_queries = list(
						declared_xpath_query['name'] for declared_xpath_query in self.config["xpath_queries"][query_host]
					)

					# We get the query attribute 'name', this will later translate into self.'name'

					xpath_query_name = xpath_query.getAttribute("name").strip().lower()

					if not xpath_query_name:

						# Attribute 'name' is missing. Every query must have a name, program halted

						self.messages.raise_error(self.messages.EMPTY_XML_TAG_ATTR % {
							"xml_tag_attr" : "query['name']",
							"path_to_xml" : self.config["path_to_config"]
						}, self.messages.INTERNAL)

					if xpath_query_name == "none":

						self.messages.raise_error(self.messages.XPATH_NONE_NAME % {
							"path_to_xml" : self.config["path_to_config"]
						}, self.messages.INTERNAL)

					# Because the attribute 'name' will later translate into a variable, it must be a valid identifier
					# Therefore we validate the name

					if not self.validation.validate_identifier(xpath_query_name):

						# The name is not a valid Python identifier and will, most likely, cause problems later
						# Program halted

						self.messages.raise_error(self.messages.INVALID_IDENTIFIER % {
							"identifier" : "query['" + xpath_query_name + "']",
							"path_to_xml" : self.config["path_to_config"]
						}, self.messages.INTERNAL)

					# We get the query attribute 'context' and validate its content

					xpath_query_context = xpath_query.getAttribute("context").strip().lower()

					if not xpath_query_context or xpath_query_context == "none":

						# If it doesn't exists, it's empty or 'none' we default to None
						# No warnings needed as it is an opcional attribute

						xpath_query_context = None

					# We get the query attribute 'get_value' and validate its content

					xpath_get_value = xpath_query.getAttribute("get_value").strip().lower()

					if not xpath_get_value or xpath_get_value == "false":

						# If it doesn't exists, it's empty or 'false' we default to False
						# No warnings needed as it is an opcional attribute

						xpath_get_value = False

					elif xpath_get_value == "true":

						xpath_get_value = True

					else:

						# The content of the attribute 'xpath_get_value' is invalid (!= 'true' | 'false' | empty | '')
						# We default to false and issue a warning

						xpath_get_value = False

						self.messages.issue_warning(self.messages.INVALID_ATTR_VALUE % {
							"attr_value" : xpath_get_value,
							"attr" : "get_value",
							"path_to_xml" : self.config["path_to_config"]
						}, self.messages.INTERNAL)

					if not xpath_query.firstChild or not xpath_query.firstChild.nodeValue.strip():

						# The XPath query is empty and it shouldn't, program halted

						self.messages.raise_error(self.messages.EMPTY_XML_TAG_VALUE % {
							"xml_tag_name" : "query['" + xpath_query_name + "']",
							"path_to_xml" : self.config["path_to_config"]
						}, self.messages.INTERNAL)

					query = xpath_query.firstChild.nodeValue.strip()
			
					if xpath_query_name in declared_xpath_queries:

						# There are two XPath queries with the same name
						# That shouldn't happen as every query name must be unique, program halted

						self.messages.raise_error(self.messages.XPATH_DUPLICATED_QUERY % {
							"xpath_query_name" : xpath_query_name,
							"path_to_xml" : self.config["path_to_config"]
						}, self.messages.INTERNAL)

					if not xpath_query_context in [None] + declared_xpath_queries:

						# The XPath query context isn't defined
						# That shouldn't happen as every context must be defined as a query beforehand
						# Program halted

						self.messages.raise_error(self.messages.XPATH_CONTEXT_NOT_DEFINED % {
							"xpath_query_context" : xpath_query_context,
							"path_to_xml" : self.config["path_to_config"]
						}, self.messages.INTERNAL)

					# We proceed to test the XPath query in the sandbox

					try:

						self.xpath.find(query, sandbox, False, None, [])

					except XPathNotImplementedError:

						self.messages.raise_error(self.messages.XPATH_FEATURE_NOT_IMPLEMENTED % {
							"query" : query
						}, self.messages.INTERNAL)

					except XPathParseError:

						self.messages.raise_error(self.messages.XPATH_PARSE_ERROR % {
							"query" : query
						}, self.messages.INTERNAL)

					except XPathTypeError:

						self.messages.raise_error(self.messages.XPATH_TYPE_ERROR % {
							"query" : query
						}, self.messages.INTERNAL)

					except XPathUnknownFunctionError:

						self.messages.raise_error(self.messages.XPATH_UNKNOWN_FUNCTION_ERROR % {
							"query" : query
						}, self.messages.INTERNAL)

					except XPathUnknownPrefixError:

						self.messages.raise_error(self.messages.XPATH_UNKNOWN_PREFIX_ERROR % {
							"query" : query
						}, self.messages.INTERNAL)

					except XPathUnknownVariableError:

						self.messages.raise_error(self.messages.XPATH_UNKNOWN_VARIABLE_ERROR % {
							"query" : query
						}, self.messages.INTERNAL)

					# Finally, we append a new dictionary in the self.config["xpath_queries"][query_host]
					# There will be one dictionary per query and therefore multiple dictionaries per host
					#
					# E.g: self.config["xpath_queries"]["en.wikipedia.org"] will return all en.wikipedia.org queries
					# Or will raise a KeyError exception if there are none

					self.config["xpath_queries"][query_host].append({
						"name" : xpath_query_name,
						"context" : xpath_query_context,
						"query" : query,
						"get_value" : xpath_get_value,
						"result" : []
					})

	def __del__(self):

		# [Low] TODO

		pass

	def run(self, url, last_update = 0):

		"""
		Given an URL and a 'last update' timestamp, it applies the corresponding XPath queries to the resource content
		(assuming we're talking about a (X)HTML/XML resource) and creates a custom set of variables named after the queries
		In the XML configuration file. These custom set of variables will hold the XPath queries results

		This will only be done if and only if the 'last-modified' header of the resource is greater than the 'last_update'
		Parameter. If no 'last_update' is specified then it is defaulted to 0, forcing the visit.

		Returns the HTTP response code of the request or False if an error occurs
		"""

		# At this point 'url' must be a valid URL
		# However we revalidate it as this class is solution independent

		url = url.strip()

		if not self.validation.validate_url(url):

			# The URL is invalid. There's nothing to do, we skip the URL and move on to the next

			self.messages.issue_warning(self.messages.INVALID_URL % {
				"url" : url
			})

			return False

		# We get the host out of the URL

		host = urlparse(url)[1]

		try:

			# And 'poke' self.config["xpath_queries"][host] to see if there are any queries defined for that host

			self.config["xpath_queries"][host]

		except KeyError:

			# The host doesn't have any queries defined. There's nothing to do, we skip the URL and move on to the next

			self.messages.issue_warning(self.messages.HOST_NOT_DEFINED % {
				"host" : host,
				"url" : url
			})

			return False

		# We try to get '/robots.txt' to see if we have clearance to access the url

		try:

			if not self.request.knock(self.config["user_agent"], url, True):

				# The host has explicitly specified that he doesn't want us to fetch this URL

				self.messages.issue_warning(self.messages.ROBOT_FORBIDDEN % {
					"host" : host,
					"url" : url
				})

				return False

		except gaierror:

			# A DNS lookup error ocurred, most probably everything else will fail. Let's just end it here

			self.messages.issue_warning(self.messages.DNS_LOOKUP_FAILED % {
				"url" : url
			})

			return False

		# We need to get the resource headers in order to attempt to know if the resource has been modified since 'last_update'
		# And avoid a possible unnecessary GET request
		#
		# Since the header 'last-modified' is optional, in case it doesn't exist for any given resource (assuming a 2xx response code)
		# We must force the visit to that resource

		try:

			# We make the HEAD request

			self.request.make(
				url,
				self.request.HEAD,
				self.config["user_agent"],
				self.config["charset"]
			)

		except ResponseCodeError as response_code:

			# We got an error response code (3xx, 4xx, 5xx). We skip the URL and return the response code

			response_code = int(str(response_code))

			self.messages.issue_warning(self.messages.RESPONSE_CODE_ERROR % {
				"url" : url,
				"code" : response_code,
				"explanation" : BaseHTTPRequestHandler.responses[response_code][1]
			})

			return response_code

		except NotConnected:

			# Socket was not open and failed to open a second time automatically

			self.messages.issue_warning(self.messages.NOT_CONNECTED % {
					"host" : host,
					"url" : url
			})

			return False

		except InvalidURL:

			# A port was given and was non-numeric or empty

			self.messages.issue_warning(self.messages.INVALID_URL % {
				"url" : url
			})

			return False

		except UnknownProtocol:

			# We got a protocol that wasn't HTTP/0.9, HTTP/1.0 or HTTP/1.1

			self.messages.issue_warning(self.messages.UNKNOWN_PROTOCOL % {
				"url" : url
			})

			return False

		except UnknownTransferEncoding:

			# Currently not raised in httplib

			return False

		except UnimplementedFileMode:

			# Currently not raised in httplib

			return False

		except IncompleteRead:

			# Either there was a synch problem or the socket was interrupted by a signal (resulting in a partial read)
			# The content is corrupted and cannot be used

			self.messages.issue_warning(self.messages.INCOMPLETE_READ % {
				"url" : url
			})

			return False

		except ImproperConnectionState:

			# Either 'CannotSendRequest', 'CannotSendHeader' or 'ResponseNotReady'
			# Usually raised when doing multiple requests without reading responses between requests
			# 'ResponseNotReady' is raised when the server don't send back any headers or the socket is
			# closed/interrupted while trying to read them

			self.messages.issue_warning(self.messages.REQUEST_FAILED % {
				"url" : url
			})

			return False

		except BadStatusLine:

			# The server responded with an unknown HTTP response code (< 100 || > 999)

			self.messages.issue_warning(self.messages.BAD_STATUS_LINE % {
				"url" : url
			})

			return False

		except HTTPException:

			# Any other unknown exception is caught here

			self.messages.issue_warning(self.messages.REQUEST_FAILED % {
				"url" : url
			})

			return False

		except timeout:

			# Connection timed out

			self.messages.issue_warning(self.messages.CONNECTION_TIMED_OUT % {
				"url" : url
			})

			return False

		except gaierror:

			# Failed DNS server lookup, low level stuff.

			self.messages.issue_warning(self.messages.DNS_LOOKUP_FAILED % {
				"url" : url
			})

			return False

		if self.request.current_content_type in self.request.XML_MIME_TYPES:

			try:

				# We try to get the last-modified header from the last request
				#
				# If we reach this point we can assume the request was successful (2xx)

				last_modified = parsedate(self.request.current_headers["last-modified"])
	
			except KeyError:

				last_modified = None

				# The server didn't specified a last-modified header for the resource...

				self.messages.issue_warning(self.messages.HTTP_HEADER_MISSING % {
					"header" : "last-modified",
					"url" : url
				})

			if not last_modified:

				# ... no problem! we use the local time as last-modified and add 24 hours to force the visit

				last_modified = localtime(time() + (24 * 60 * 60))

			try:

				# We transform the 9-tuple date into a UNIX timestamp

				last_modified = mktime(last_modified) + (24 * 60 * 60)

			except OverflowError:

				# Somehow localtime() or the server returned an invalid date
				# This is very rare but it can happen

				self.messages.raise_error(self.messages.OVERFLOW_ERROR % {
					"expression" : "mktime(" + repr(last_modified) + ")"
				}, self.messages.INTERNAL)

				return False

			except ValueError:

				# Same as the former

				self.messages.raise_error(self.messages.VALUE_ERROR % {
					"expression" : "mktime(" + repr(last_modified) + ")"
				}, self.messages.INTERNAL)

				return False

			if last_modified > float(last_update):

				#URL needs to be updated

				try:

					# We make the GET request

					self.request.make(
						url,
						self.request.GET,
						self.config["user_agent"],
						self.config["charset"]
					)

				except ResponseCodeError as response_code:

					# We got an error response code (3xx, 4xx, 5xx). We skip the URL and return the response code

					response_code = int(str(response_code))

					self.messages.issue_warning(self.messages.RESPONSE_CODE_ERROR % {
						"url" : url,
						"code" : response_code,
						"explanation" : BaseHTTPRequestHandler.responses[response_code][1]
					})

					return response_code

				except NotConnected:

					# Socket was not open and failed to open a second time automatically

					self.messages.issue_warning(self.messages.NOT_CONNECTED % {
						"host" : host,
						"url" : url
					})

					return False

				except InvalidURL:

					# A port was given and was non-numeric or empty

					self.messages.issue_warning(self.messages.INVALID_URL % {
						"url" : url
					})

					return False

				except UnknownProtocol:

					# We got a protocol that wasn't HTTP/0.9, HTTP/1.0 or HTTP/1.1

					self.messages.issue_warning(self.messages.UNKNOWN_PROTOCOL % {
						"url" : url
					})

					return False

				except UnknownTransferEncoding:

					# Currently not raised in httplib

					return False

				except UnimplementedFileMode:

					# Currently not raised in httplib

					return False

				except IncompleteRead:

					# Either there was a synch problem or the socket was interrupted by a signal (resulting in a partial read)
					# The content is corrupted and cannot be used

					self.messages.issue_warning(self.messages.INCOMPLETE_READ % {
						"url" : url
					})

					return False

				except ImproperConnectionState:

					# Either 'CannotSendRequest', 'CannotSendHeader' or 'ResponseNotReady'
					# Usually raised when doing multiple requests without reading responses between requests
					# 'ResponseNotReady' is raised when the server don't send back any headers or the socket is
					# closed/interrupted while trying to read them

					self.messages.issue_warning(self.messages.REQUEST_FAILED % {
						"url" : url
					})

					return False

				except BadStatusLine:

					# The server responded with an unknown HTTP response code (< 100 || > 999)

					self.messages.issue_warning(self.messages.BAD_STATUS_LINE % {
						"url" : url
					})

					return False

				except HTTPException:

					# Any other unknown exception is caught here

					self.messages.issue_warning(self.messages.REQUEST_FAILED % {
						"url" : url
					})

					return False

				except timeout:

					# Connection timed out

					self.messages.issue_warning(self.messages.CONNECTION_TIMED_OUT % {
						"url" : url
					})

					return False

				except gaierror:

					# Failed DNS server lookup, low level stuff.

					self.messages.issue_warning(self.messages.DNS_LOOKUP_FAILED % {
						"url" : url
					})

					return False

				# XPath querying begins here (A.K.A "the interesting part")

				# xpath_main_context = whole (X)HTML/XML document. This is for those queries that doesn't
				# Have any context defined

				if self.request.current_content_type in self.request.XML_MIME_TYPES:

					xpath_main_context = minidom.parseString(self.request.current_content)

					for xpath_query in self.config["xpath_queries"][host]:

						if not xpath_query["context"]:

							self.xpath.find(
								xpath_query["query"],
								xpath_main_context,
								xpath_query["get_value"],
								self.config["charset"],
								xpath_query["result"]
							)

						else:

							for query in self.config["xpath_queries"][host]:

								if query['name'] == xpath_query["context"]:

									xpath_context = query['result']

									break

							for context in xpath_context:

								if not context:

									context = "<_/>"

								node = minidom.parseString(context)

								self.xpath.find(
									xpath_query["query"],
									node,
									xpath_query["get_value"],
									self.config["charset"],
									xpath_query["result"]
								)

						vars(self)[xpath_query["name"]] = xpath_query["result"]

					# We need to clean the queries results in order to allow subsequent 'self.run' calls
					# These results are already stored in their respective variables

					for xpath_query in self.config["xpath_queries"][host]:

						xpath_query["result"] = []

				else:

					# The resource is not an (X)HTML/XML resource, we issue a warning and skip the URL

					self.messages.issue_warning(self.messages.MIME_TYPE_NOT_SUPPORTED % {
						"url" : url,
						"mime-type" : self.request.current_content_type
					})

			else:

				# URL is up-to-date, we issue a warning indicating this (so it can be logged) and skip the URL

				self.messages.issue_warning(self.messages.URL_NOT_MODIFIED % {
					"url" : url
				})

		else:

			# The resource is not an (X)HTML/XML resource, we issue a warning and skip the URL

			self.messages.issue_warning(self.messages.MIME_TYPE_NOT_SUPPORTED % {
				"url" : url,
				"mime-type" : self.request.current_content_type
			})

		return self.request.current_response_code
