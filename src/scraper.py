
"""Core libraries, do not change"""

# Native
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from urlparse import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler
from rfc822 import parsedate
from time import localtime, mktime
from socket import gaierror

# User defined
from messages import Messages
from helpers.validation import Validation
from helpers.request import Request, ResponseCodeError

# External
import xpath, tidy

"""User defined libraries goes here""""

# Native
from urlparse import parse_qs

class Scraper:

	config = {
		"path_to_config" : "../config/scraper.xml",
		"xpath_queries" : {},
		"user_agent" : None
	}

	tidy_options = {
		"output_xhtml" : True,
		"add_xml_decl" : True,
		"bare" : True,
		"drop_empty_paras" : True,
		"drop_proprietary_attributes" : True,
		"escape_cdata" : True,
		"hide_comments" : True,
		"join_classes" : True,
		"char_encoding" : "utf8",
		"output_bom" : True
	}

	messages = Messages()

	validation = Validation()

	request = Request()

	def __init__(self):

		"""Contructor"""

		# We try to open the xml configuration file (self.config["path_to_config"]) and parse it
		# WE WILL NOT TIDY IT, it must be a valid XML file

		try:

			dom = minidom.parse(self.config["path_to_config"])

		except IOError:

			# I/O error, e.g: open/read/race conditions, low level stuff

			self.messages.raise_error(self.messages.XML_CONFIG_IO_ERROR % {
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		except ExpatError:

			# Invalid XML file

			self.messages.raise_error(self.messages.INVALID_XML_FILE % {
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		# Now that the file is open we try to get the root node ('scraper') from the XML configuration file

		try:

			root = dom.getElementsByTagName("scraper")[0]

		except IndexError:

			# The 'scraper' tag is missing 

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "scraper",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		# We try to get the user agent name string from the XML configuration file

		try:

			user_agent = root.getElementsByTagName("general")[0].getElementsByTagName("user_agent")

		except IndexError:

			# The 'general' tag containing the 'user_agent' tag is missing

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "general",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		# We 'poke' the variable user_agent[0] to see if there is a 'user_agent' tag defined in the XML configuration file

		try:

			user_agent[0]

		except IndexError:

			# The tags 'user_agent' is missing

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "user_agent",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		# We verify that the 'user_agent' tag content exists and is not an empty (whitespace) string

		if not user_agent[0].firstChild or not user_agent[0].firstChild.nodeValue.strip():

			# 'user_agent' tag content doesn't exists or is an empty string (whitespace)

			self.messages.raise_error(self.messages.EMPTY_XML_TAG_VALUE % {
				"xml_tag_name" : "user_agent",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		self.config["user_agent"] = user_agent[0].firstChild.nodeValue.strip()

		# We try to get the XPath queries found in 'xpath' > 'queries'

		try:

			queries = root.getElementsByTagName("xpath")[0].getElementsByTagName("queries")

		except IndexError:

			# 'xpath' tag is missing

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "xpath",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		if not queries:

			# 'queries' tag is missing

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "queries",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		for query in queries:

			# We need to associate every set of queries to one or serveral hosts
			# So we get the 'hosts' attribute, clean it and create a list of hosts for the current 'queries' tag

			query_hosts = query.getAttribute("hosts").strip().lower().split(",")

			query_hosts = filter(None, query_hosts)

			query_hosts = list(
				query_host.strip() for query_host in query_hosts
			)

			if not query_hosts:

				# Attribute 'hosts' was not specified or was empty

				self.messages.raise_error(self.messages.EMPTY_XML_TAG_ATTR % {
					"xml_tag_attr" : "queries['hosts']",
					"path_to_xml" : self.config["path_to_config"]
				}, self.messages.INTERNAL)

			# We get the current set of queries corresponding to the lasts hosts

			xpath_queries = query.getElementsByTagName("query")

			if not xpath_queries:

				# 'query' tag is missing

				self.messages.raise_error(self.messages.XML_TAG_MISSING % {
					"xml_tag_name" : "query",
					"path_to_xml" : self.config["path_to_config"]
				}, self.messages.INTERNAL)

			for query_host in query_hosts:

				# We treat every host independently so it will have its own set of queries

				self.config["xpath_queries"][query_host] = []

				for xpath_query in xpath_queries:

					# We need to have a list of used query names to avoid duplicates

					declared_xpath_queries = list(
						declared_xpath_query['name'] for declared_xpath_query in self.config["xpath_queries"][query_host]
					)

					# We get the query attribute 'name', this will later translate into self.'name'

					xpath_query_name = xpath_query.getAttribute("name").strip().lower()

					if not xpath_query_name:

						# Attribute 'name' is missing

						self.messages.raise_error(self.messages.EMPTY_XML_TAG_ATTR % {
							"xml_tag_attr" : "query['name']",
							"path_to_xml" : self.config["path_to_config"]
						}, self.messages.INTERNAL)

					# Because the attribute 'name' will later translate into a variable, it must be a valid identifier
					# Therefore we validate the name

					if not self.validation.validate_identifier(xpath_query_name):

						self.messages.raise_error(self.messages.INVALID_IDENTIFIER % {
							"identifier" : "query['" + xpath_query_name + "']",
							"path_to_xml" : self.config["path_to_config"]
						}, self.messages.INTERNAL)

					# We get the query attribute 'context' and validate its content

					xpath_query_context = xpath_query.getAttribute("context").strip().lower()

					if not xpath_query_context or xpath_query_context == "none":

						xpath_query_context = None

					# We get the query attribute 'get_value' and validate its content

					xpath_get_value = xpath_query.getAttribute("get_value").strip().lower()

					if not xpath_get_value or xpath_get_value == "false":

						xpath_get_value = False

					elif xpath_get_value == "true":

						xpath_get_value = True

					else:

						# The value of the query attribute 'context' is invalid
						# We default to false and issue a warning

						xpath_get_value = False

						self.messages.issue_warning(self.messages.INVALID_ATTR_VALUE % {
							"attr_value" : xpath_get_value,
							"attr" : "get_value",
							"path_to_xml" : self.config["path_to_config"]
						}, self.messages.INTERNAL)

					if not xpath_query.firstChild or not xpath_query.firstChild.nodeValue.strip():

						# The XPath query is empty and it shouldn't

						self.messages.raise_error(self.messages.EMPTY_XML_TAG_VALUE % {
							"xml_tag_name" : "query['" + xpath_query_name + "']",
							"path_to_xml" : self.config["path_to_config"]
						}, self.messages.INTERNAL)
			
					if xpath_query_name in declared_xpath_queries:

						# There are two XPath queries with the same name
						# That shouldn't happen

						self.messages.raise_error(self.messages.XPATH_DUPLICATED_QUERY % {
							"xpath_query_name" : xpath_query_name,
							"path_to_xml" : self.config["path_to_config"]
						}, self.messages.INTERNAL)

					if not xpath_query_context in [None] + declared_xpath_queries:

						# The XPath query context isn't defined
						# That shouldn't happen

						self.messages.raise_error(self.messages.XPATH_CONTEXT_NOT_DEFINED % {
							"xpath_query_context" : xpath_query_context,
							"path_to_xml" : self.config["path_to_config"]
						}, self.messages.INTERNAL)

					# Finally, we append a new dictionary in the self.config["xpath_queries"][query_host]
					# There will be one dictionary per query and therefore multiple dictionaries per host
					#
					# E.g: self.config["xpath_queries"]["en.wikipedia.org"] will return all en.wikipedia.org queries
					# Or will raise a KeyError exception if there are none

					self.config["xpath_queries"][query_host].append({
						"name" : xpath_query_name,
						"context" : xpath_query_context,
						"query" : xpath_query.firstChild.nodeValue.strip(),
						"get_value" : xpath_get_value,
						"result" : []
					})

	def __del__(self):

		#TODO

		pass

	def run(self, url, last_update):

		"""
		Given an URL and a 'last update' timestamp, it applies the corresponding XPath queries to the resource content
		(assuming we're talking about a (X)HTML resource) and creates a custom set of variables named after the queries
		in the XML configuration file. These custom set of variables will hold the XPath queries results.
		"""

		#At this point 'url' is a valid URL, there's no need to re-validate it

		host = urlparse(url)[1]

		try:

			self.config["xpath_queries"][host]

		except KeyError:

			self.messages.issue_warning(self.messages.HOST_NOT_DEFINED % {
				"host" : host,
				"url" : url
			})

			return False

		#TODO: except httplib exceptions

		try:

			self.request.make(self.request.HEAD, url, self.config["user_agent"])

		except ResponseCodeError as response_code:

			response_code = int(str(response_code))

			self.messages.issue_warning(self.messages.RESPONSE_CODE_ERROR % {
				"url" : url,
				"code" : response_code,
				"explanation" : BaseHTTPRequestHandler.responses[response_code][1]
			})

			#TODO: take decisions based on response_code

			return False

		except gaierror:

			self.messages.issue_warning(self.messages.CONNECTION_PROBLEM % {
				"url" : url
			}, self.messages.INTERNAL)

			return False

		try:

			last_modified = parsedate(self.request.current_headers["last-modified"])
	
		except KeyError:

			self.messages.issue_warning(self.messages.HTTP_HEADER_MISSING % {
				"header" : "last-modified",
				"url" : url
			})

			last_modified = None

		if not last_modified:

			last_modified = localtime()

		try:

			last_modified = mktime(last_modified)

		except OverflowError:

			self.messages.raise_error(self.messages.OVERFLOW_ERROR % {
				"expression" : "mktime(" + repr(last_modified) + ")"
			}, self.messages.INTERNAL)

		except ValueError:

			self.messages.raise_error(self.messages.VALUE_ERROR % {
				"expression" : "mktime(" + repr(last_modified) + ")"
			}, self.messages.INTERNAL)

		if last_modified >= float(last_update):

			#URL needs to be updated

			#TODO: except httplib exceptions

			try:

				self.request.make(self.request.GET, url, self.config["user_agent"])

			except ResponseCodeError as response_code:

				response_code = int(str(response_code))

				self.messages.issue_warning(self.messages.RESPONSE_CODE_ERROR % {
					"url" : url,
					"code" : response_code,
					"explanation" : BaseHTTPRequestHandler.responses[response_code][1]
				})

				#TODO: take decisions based on response_code

				return False

			except gaierror:

				self.messages.issue_warning(self.messages.CONNECTION_PROBLEM % {
					"url" : url
				}, self.messages.INTERNAL)

				return False

			#XPath begins here

			xpath_main_context = minidom.parseString(
				str(
					tidy.parseString(self.request.current_xhtml, **self.tidy_options)
				)
			)


			for xpath_query in self.config["xpath_queries"][host]:

				#TODO: except all XPath errors
				
				xpath_results = []

				if not xpath_query["context"]:

					xpath_results.append(xpath.find(xpath_query["query"], xpath_main_context))

				else:

					xpath_contexts = list(
						query for query in self.config["xpath_queries"][host] if query["name"] == xpath_query["context"]
					)[0]["result"]

					if xpath_contexts:

						for xpath_context in xpath_contexts:

							for node in xpath_context:

								node = minidom.parseString(node.toxml("UTF-8"))

								if xpath_query["get_value"]:

									xpath_results.append(xpath.findvalue(xpath_query["query"], node))

								else:

									xpath_results.append(xpath.find(xpath_query["query"], node))

				if xpath_results:

					xpath_query["result"] = xpath_results

			for index in range(len(self.config["xpath_queries"][host])):

				vars(self)[self.config["xpath_queries"][host][index]["name"]] = self.config["xpath_queries"][host][index]["result"]

			"""At this point you have a set of variables matching your queries specification. All the extra logic goes here"""

			for revision in range(len(self.revision[0])):

				print "Revision " + str(revision + 1) + ":"

				print "-meadiawiki id: " + parse_qs(self.mediawiki_id[revision][0].nodeValue)["oldid"][0]

				print "-date: " + repr(self.date[revision])

				print "-user: " + repr(self.user[revision])

				print "-minor: " + repr(self.minor[revision])

				print "-size: " + repr(self.size[revision])

				print "-comment: " + repr(self.comment[revision])

			#Debug
			#pp = pprint.PrettyPrinter(indent=4)
			#pp.pprint(self.config["xpath_queries"][host])

		else:

			#URL is up-to-date

			self.messages.issue_warning(self.messages.URL_NOT_MODIFIED % {
				"url" : url
			})
