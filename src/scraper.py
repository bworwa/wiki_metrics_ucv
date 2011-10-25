#Native
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from urlparse import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler
from rfc822 import parsedate
from time import localtime, mktime
from socket import gaierror
from re import findall, sub

#User defined
from messages import Messages
from helpers.validation import Validation
from helpers.request import Request, ResponseCodeError

#external
import xpath, tidy

#debug
import pprint

class Scraper:

	config = {
		"path_to_config" : "../config/scraper.xml",
		"xpath_queries" : {},
		"user_agent" : None
	}

	#TODO: check all the options
	tidy_options = {
		"output_xhtml" : True,
		"bare" : True,
		"drop_empty_paras" : True,
		"drop_proprietary_attributes" : True,
		"escape_cdata" : True,
		"hide_comments" : True,
		"join_classes" : True,
		"char_encoding" : "utf8",
	}

	messages = Messages()

	validation = Validation()

	request = Request()

	def __init__(self):

		#We try to open the xml configuration file (^) and parse it
		try:

			dom = minidom.parse(self.config["path_to_config"])

		except IOError:

			self.messages.raise_error(self.messages.XML_CONFIG_IO_ERROR % {
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		except ExpatError:

			self.messages.raise_error(self.messages.INVALID_XML_FILE % {
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		#Now that the file is open we try to get the root node ('scraper')

		try:

			root = dom.getElementsByTagName("scraper")[0]

		except IndexError:

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "scraper",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		#from there we try to get the user agent name string
		try:

			user_agent = root.getElementsByTagName("general")[0].getElementsByTagName("user_agent")

		except IndexError:

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "general",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		try:

			user_agent[0]

		except IndexError:

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "user_agent",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		if not user_agent[0].firstChild or not user_agent[0].firstChild.nodeValue.strip():

			self.messages.raise_error(self.messages.EMPTY_XML_TAG_VALUE % {
				"xml_tag_name" : "user_agent",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		self.config["user_agent"] = user_agent[0].firstChild.nodeValue.strip()

		#After that we proceed with the XPath queries
		try:

			queries = root.getElementsByTagName("xpath")[0].getElementsByTagName("queries")

		except IndexError:

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "xpath",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		if not queries:

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "queries",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		for query in queries:

			query_hosts = query.getAttribute("hosts").lower().split(",")

			query_hosts = filter(None, query_hosts)

			query_hosts = list(
				query_host.strip() for query_host in query_hosts
			)

			if not query_hosts:

				self.messages.raise_error(self.messages.EMPTY_XML_TAG_ATTR % {
					"xml_tag_attr" : "queries['hosts']",
					"path_to_xml" : self.config["path_to_config"]
				}, self.messages.INTERNAL)

			xpath_queries = query.getElementsByTagName("query")

			if not xpath_queries:

				self.messages.raise_error(self.messages.XML_TAG_MISSING % {
					"xml_tag_name" : "query",
					"path_to_xml" : self.config["path_to_config"]
				}, self.messages.INTERNAL)

			for query_host in query_hosts:

				self.config["xpath_queries"][query_host] = []

				for xpath_query in xpath_queries:

					declared_xpath_queries = list(
						declared_xpath_query['name'] for declared_xpath_query in self.config["xpath_queries"][query_host]
					)

					xpath_query_name = xpath_query.getAttribute("name").lower()

					if not xpath_query_name:

						self.messages.raise_error(self.messages.EMPTY_XML_TAG_ATTR % {
							"xml_tag_attr" : "query['name']",
							"path_to_xml" : self.config["path_to_config"]
						}, self.messages.INTERNAL)

					if not self.validation.validate_identifier(xpath_query_name):

						self.messages.raise_error(self.messages.INVALID_IDENTIFIER % {
							"identifier" : "query['" + xpath_query_name + "']",
							"path_to_xml" : self.config["path_to_config"]
						}, self.messages.INTERNAL)

					xpath_query_context = xpath_query.getAttribute("context").lower()

					if not xpath_query_context or xpath_query_context in ["none"]:

						xpath_query_context = None

					if not xpath_query.firstChild or not xpath_query.firstChild.nodeValue.strip():

						self.messages.raise_error(self.messages.EMPTY_XML_TAG_VALUE % {
							"xml_tag_name" : "query['" + xpath_query_name + "']",
							"path_to_xml" : self.config["path_to_config"]
						}, self.messages.INTERNAL)
			
					if xpath_query_name in declared_xpath_queries:

						self.messages.raise_error(self.messages.XPATH_DUPLICATED_QUERY % {
							"xpath_query_name" : xpath_query_name,
							"path_to_xml" : self.config["path_to_config"]
						}, self.messages.INTERNAL)

					if not xpath_query_context in [None] + declared_xpath_queries:

						self.messages.raise_error(self.messages.XPATH_CONTEXT_NOT_DEFINED % {
							"xpath_query_context" : xpath_query_context,
							"path_to_xml" : self.config["path_to_config"]
						}, self.messages.INTERNAL)

					self.config["xpath_queries"][query_host].append({
						"name" : xpath_query_name,
						"context" : xpath_query_context,
						"query" : xpath_query.firstChild.nodeValue.strip(),
						"result" : []
					})

	def __del__(self):

		#TODO

		pass

	def run(self, url, last_update):

		#At this point 'url' is a valid URL, there's no need to validate it

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

							for element in xpath_context:

								element = minidom.parseString(element.toxml("UTF-8"))

								xpath_results.append(xpath.find(xpath_query["query"], element))

				if xpath_results:

					xpath_query["result"] = xpath_results

			for index in range(len(self.config["xpath_queries"][host])):

				vars(self)[self.config["xpath_queries"][host][index]["name"]] = self.config["xpath_queries"][host][index]["result"]

			"""At this point you have a set of variables matching your queries specification. All the extra logic goes here"""

			for revision in range(len(self.revisions[0])):

				print "Revision:"

				print "-meadiawiki id: " + findall("oldid=[0-9]+", self.mediawiki_id[revision][0].toxml())[0].replace("oldid=", "").strip()

				print "-user: " + sub("<[^>]*?>", "", self.user[revision][0].toxml()).strip()

				if self.minor[revision]:

					print "-minor: True"

				else:

					print "-minor: False"

				print "-size: " + sub("<[^>]*?>", "", self.size[revision][0].toxml()).strip()

				if self.comment[revision]:

					print "-comment: " + sub("<[^>]*?>", "", self.comment[revision][0].toxml()).strip()

			#Debug
			#pp = pprint.PrettyPrinter(indent=4)
			#pp.pprint(self.config["xpath_queries"][host])

		else:

			#URL is up-to-date

			self.messages.issue_warning(self.messages.URL_NOT_MODIFIED % {
				"url" : url
			})
