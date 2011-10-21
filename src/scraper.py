#Native
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from messages import Messages
from urlparse import urlparse

#User defined
from helpers import validation, request

class Scraper:

	config = {
		"path_to_config" : "../config/scraper.xml",
		"xpath_queries" : {},
		"user_agent" : None
	}

	current_headers = None

	messages = Messages()

	validation = validation.Validation()

	request = request.Request()

	def __init__(self):

		global minidom

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

		#Now that the file is open we try to get the user-agent name string
		try:

			user_agent = dom.getElementsByTagName("general")[0].getElementsByTagName("user_agent")

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

		if not user_agent[0].firstChild.nodeValue.strip():

			self.messages.raise_error(self.messages.EMPTY_XML_TAG_VALUE % {
				"xml_tag_name" : "user_agent",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		self.config["user_agent"] = user_agent[0].firstChild.nodeValue.strip()

		#After that we proceed with the XPath queries
		try:

			queries = dom.getElementsByTagName("xpath")[0].getElementsByTagName("queries")

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

					if not xpath_query.firstChild.nodeValue.strip():

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
						"result" : None
					})

	def __del__(self):

		#TODO

		pass

	def run(self, url):

		#At this point 'url' is a valid URL, no need to validate it

		host = urlparse(url)[1]

		try:

			self.config["xpath_queries"][host]

			self.request.head(url, self.config["user_agent"])

			print self.request.current_headers

		except KeyError:

			self.messages.issue_warning(self.messages.HOST_NOT_DEFINED % {
				"host" : host
			})
