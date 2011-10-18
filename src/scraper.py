from xml.dom import minidom
from xml.parsers.expat import ExpatError
from messages import Messages
from urlparse import urlparse
from helpers import validation

class Scraper:

	config = { "xpath_queries" : {} }
	messages = Messages()

	def __init__(self):

		global minidom

		path_to_xml = "../config/scraper.xml"

		try:

			dom = minidom.parse(path_to_xml)

		except IOError:

			self.messages.raise_error(self.messages.XML_CONFIG_IO_ERROR % {
				"path_to_xml" : path_to_xml
			}, self.messages.INTERNAL)

		except ExpatError:

			self.messages.raise_error(self.messages.INVALID_XML_FILE % {
				"path_to_xml" : path_to_xml
			}, self.messages.INTERNAL)

		try:

			queries = dom.getElementsByTagName("xpath")[0].getElementsByTagName("queries")

		except IndexError:

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "xpath",
				"path_to_xml" : path_to_xml
			}, self.messages.INTERNAL)

		if not queries:

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "queries",
				"path_to_xml" : path_to_xml
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
					"path_to_xml" : path_to_xml
				}, self.messages.INTERNAL)

			xpath_queries = query.getElementsByTagName("query")

			if not xpath_queries:

				self.messages.raise_error(self.messages.XML_TAG_MISSING % {
					"xml_tag_name" : "query",
					"path_to_xml" : path_to_xml
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
							"path_to_xml" : path_to_xml
						}, self.messages.INTERNAL)

					if not validation.validate_identifier(xpath_query_name):

						self.messages.raise_error(self.messages.INVALID_IDENTIFIER % {
							"identifier" : "query['" + xpath_query_name + "']",
							"path_to_xml" : path_to_xml
						}, self.messages.INTERNAL)

					xpath_query_context = xpath_query.getAttribute("context").lower()

					if not xpath_query_context or xpath_query_context in ["none"]:

						xpath_query_context = None

					if not xpath_query.firstChild:

						self.messages.raise_error(self.messages.EMPTY_XML_TAG_VALUE % {
							"xml_tag_name" : "query['" + xpath_query_name + "']",
							"path_to_xml" : path_to_xml
						}, self.messages.INTERNAL)
			
					if xpath_query_name in declared_xpath_queries:

						self.messages.raise_error(self.messages.XPATH_DUPLICATED_QUERY % {
							"xpath_query_name" : xpath_query_name,
							"path_to_xml" : path_to_xml
						}, self.messages.INTERNAL)

					if not xpath_query_context in [None] + declared_xpath_queries:

						self.messages.raise_error(self.messages.XPATH_CONTEXT_NOT_DEFINED % {
							"xpath_query_context" : xpath_query_context,
							"path_to_xml" : path_to_xml
						}, self.messages.INTERNAL)

					self.config["xpath_queries"][query_host].append({
						"name" : xpath_query_name,
						"context" : xpath_query_context,
						"query" : xpath_query.firstChild.nodeValue,
						"result" : None
					})

		del dom, minidom, queries, query, query_hosts, query_host, xpath_queries, xpath_query, declared_xpath_queries
		del xpath_query_name, xpath_query_context, path_to_xml

	def __del__(self):

		#TODO

		pass

	def run(self, url):

		#At this point 'url' is a valid URL, no need to validate it

		host = urlparse(url)[1]

		try:

			self.config["xpath_queries"][host]

		except KeyError:

			self.messages.issue_warning(self.messages.HOST_NOT_DEFINED % {
				"host" : host
			})

		del url, host
