from xml.dom import minidom
from xml.parsers.expat import ExpatError
from sys import exit
from messages import Messages
from helpers import validator

class Scraper:

	config = { "xpath_queries" : [] }
	messages = Messages()

	def __init__(self):

		global minidom

		path_to_xml = "../config/scraper.xml"

		try:

			dom = minidom.parse(path_to_xml)

		except IOError:

			self.messages.raise_error(self.messages.XML_CONFIG_IO_ERROR % { "path_to_xml" : path_to_xml })

		except ExpatError:

			self.messages.raise_error(self.messages.INVALID_XML_FILE % { "path_to_xml" : path_to_xml })

		try:

			xpath_queries = dom.getElementsByTagName("xpath")[0].getElementsByTagName("queries")[0].getElementsByTagName("query")

		except IndexError:

			self.messages.raise_error(self.messages.XML_TAG_MISSING % { "xml_tag_name" : "queries", "path_to_xml" : path_to_xml })

		if not xpath_queries:

			self.messages.raise_error(self.messages.XML_TAG_MISSING % { "xml_tag_name" : "query", "path_to_xml" : path_to_xml })

		for xpath_query in xpath_queries:

			declared_xpath_queries = list((declared_xpath_query['name']) for declared_xpath_query in self.config["xpath_queries"])

			xpath_query_name = xpath_query.getAttribute("name").lower()

			if not xpath_query_name:

				self.messages.raise_error(self.messages.EMPTY_XML_TAG_ATTR % { "xml_tag_attr" : "query['name']", "path_to_xml" : path_to_xml })

			if not validator.validate_identifier(xpath_query_name):

				self.messages.raise_error(self.messages.INVALID_IDENTIFIER % { "identifier" : "query['" + xpath_query_name + "']", "path_to_xml" : path_to_xml })

			xpath_query_context = xpath_query.getAttribute("context").lower()

			if not xpath_query_context or xpath_query_context == "none":
				xpath_query_context = None

			if not xpath_query.firstChild:

				self.messages.raise_error(self.messages.EMPTY_XML_TAG_VALUE % { "xml_tag_name" : "query['" + xpath_query_name + "']", "path_to_xml" : path_to_xml })
			
			if xpath_query_name in declared_xpath_queries:

				self.messages.raise_error(self.messages.XPATH_DUPLICATED_QUERY % { "xpath_query_name" : xpath_query_name, "path_to_xml" : path_to_xml })

			if not xpath_query_context in [None] + declared_xpath_queries:

				self.messages.raise_error(self.messages.XPATH_CONTEXT_NOT_DEFINED % { "xpath_query_context" : xpath_query_context, "path_to_xml" : path_to_xml })

			self.config["xpath_queries"].append({
				"name" : xpath_query_name,
				"context" : xpath_query_context,
				"query" : xpath_query.firstChild.nodeValue,
				"result" : None
			})

		del dom, minidom, xpath_queries, xpath_query, declared_xpath_queries, xpath_query_name, xpath_query_context, path_to_xml

	def scrap(self, url):

		del url
