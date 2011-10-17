from xml.dom import minidom
from xml.parsers.expat import ExpatError
from sys import exit, stderr
from helpers import validator, logger

class Messages:

	"""Basic set of messages, these will be overwritten later with the ones in the 'messages' XML file"""

	XML_CONFIG_IO_ERROR	= "There was a problem while opening the XML configuration file '%(path_to_xml)s'"
	GENERIC_FILE_IO_ERROR	= "There was a problem while opening the file '%(path_to_file)s'"
	INVALID_XML_FILE	= "'%(path_to_xml)s' is an invalid XML file"
	XML_TAG_MISSING		= "'%(xml_tag_name)s' tag is missing in the XML configuration file '%(path_to_xml)s'"
	EMPTY_XML_TAG_ATTR	= "The tag attribute '%(xml_tag_attr)s' cannot be empty in '%(path_to_xml)s'"
	EMPTY_XML_TAG_VALUE	= "The tag '%(xml_tag_name)s' cannot be empty in '%(path_to_xml)s'"
	INVALID_IDENTIFIER	= "'%(identifier)s' is an invalid identifier ('%(path_to_xml)s')"
	
	def __init__(self):

		global minidom, exit

		path_to_xml = "../config/messages.xml"

		try:

			dom = minidom.parse(path_to_xml)

		except IOError:

			self.raise_error(self.XML_CONFIG_IO_ERROR % { "path_to_xml" : path_to_xml }, True)

		except ExpatError:

			self.raise_error(self.INVALID_XML_FILE % { "path_to_xml" : path_to_xml }, True)

		try:

			messages = dom.getElementsByTagName("messages")[0].getElementsByTagName("message")

		except IndexError:

			self.raise_error(self.XML_TAG_MISSING % { "xml_tag_name" : "messages", "path_to_xml" : path_to_xml }, True)

		if not messages:

			self.raise_error(self.XML_TAG_MISSING % { "xml_tag_name" : "message", "path_to_xml" : path_to_xml }, True)

		for message in messages:

			message_name = message.getAttribute("name").strip().upper()

			if not message_name:

				self.raise_error(self.EMPTY_XML_TAG_ATTR % { "xml_tag_attr" : "message['name']", "path_to_xml" : path_to_xml }, True)

			if not validator.validate_identifier(message_name):

				self.raise_error(self.INVALID_IDENTIFIER % { "identifier" : "message['" + message_name + "']", "path_to_xml" : path_to_xml }, True)

			if not message.firstChild:

				self.raise_error(self.EMPTY_XML_TAG_VALUE % { "xml_tag_name" : "message['" + message_name + "']", "path_to_xml" : path_to_xml }, True)

			vars(self)[message_name] = message.firstChild.nodeValue.strip(" .")

		del minidom, exit, path_to_xml, dom, messages, message, message_name

	def raise_error(self, message, internal = False):

		message = "Error: " + message + ".\n"

		stderr.write(message)

		try:

			logger.log_this(message, internal)

		except IOError:

			self.issue_warning(self.GENERIC_FILE_IO_ERROR % { "path_to_file" : logger.path_to_log }, True)

		del message

		exit(1)

	def issue_warning(self, message, internal = False):

		message = "Warning: " + message + ".\n"

		stderr.write(message)

		try:

			logger.log_this(message, internal)

		except IOError:

			pass

		del message
