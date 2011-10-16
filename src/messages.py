from xml.dom import minidom
from xml.parsers.expat import ExpatError
from sys import exit
from helpers import validator

class Messages:

	"""Basic set of messages, these will be overwritten later with the ones in the 'messages' XML file"""

	XML_CONFIG_IO_ERROR	= "There was a problem while reading the XML configuration file ('%(path_to_xml)s')"
	INVALID_XML_FILE	= "'%(path_to_xml)s' is an invalid XML file"
	XML_TAG_MISSING		= "'%(xml_tag_name)s' tag is missing in the XML configuration file ('%(path_to_xml)s')"
	EMPTY_XML_TAG_ATTR	= "The tag attribute '%(xml_tag_attr)s' cannot be empty in '%(path_to_xml)s'"
	EMPTY_XML_TAG_VALUE	= "The tag '%(xml_tag_name)s' cannot be empty in '%(path_to_xml)s'"
	INVALID_IDENTIFIER	= "'%(identifier)s' is an invalid identifier ('%(path_to_xml)s')"
	
	def __init__(self):

		global minidom, exit

		path_to_xml = "../config/messages.xml"

		try:

			dom = minidom.parse(path_to_xml)

		except IOError:

			self.raise_error(self.XML_CONFIG_IO_ERROR % { "path_to_xml" : path_to_xml })

		except ExpatError:

			self.raise_error(self.INVALID_XML_FILE % { "path_to_xml" : path_to_xml })

		try:

			messages = dom.getElementsByTagName("messages")[0].getElementsByTagName("message")

		except IndexError:

			self.raise_error(self.XML_TAG_MISSING % { "xml_tag_name" : "messages", "path_to_xml" : path_to_xml })

		if not messages:

			self.raise_error(self.XML_TAG_MISSING % { "xml_tag_name" : "message", "path_to_xml" : path_to_xml })

		for message in messages:

			message_name = message.getAttribute("name").strip().upper()

			if not message_name:

				self.raise_error(self.EMPTY_XML_TAG_ATTR % { "xml_tag_attr" : "message['name']", "path_to_xml" : path_to_xml })

			if not validator.validate_identifier(message_name):

				self.raise_error(self.INVALID_IDENTIFIER % { "identifier" : "message['" + message_name + "']", "path_to_xml" : path_to_xml })

			if not message.firstChild:

				self.raise_error(self.EMPTY_XML_TAG_VALUE % { "xml_tag_name" : "message['" + message_name + "']", "path_to_xml" : path_to_xml })

			vars(self)[message_name] = message.firstChild.nodeValue.strip(" .")

		del minidom, exit, path_to_xml, dom, messages, message, message_name

	def raise_error(self, message):
		
		exit("Error: " + message + ".")

		del message
