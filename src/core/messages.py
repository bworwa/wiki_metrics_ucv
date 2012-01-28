
"""Core libraries, do not change"""

# Native
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from sys import exit, stderr, stdout
from string import whitespace
from os.path import abspath, dirname

# XCraper
from helpers.validation import Validation
from helpers.log import Log

class Messages:

	"""Basic set of messages, these will be overwritten later with the ones in the 'messages' XML file"""

	XML_CONFIG_IO_ERROR	= "There was a problem while opening/reading the XML configuration file '%(path_to_xml)s'"
	GENERIC_FILE_IO_ERROR	= "There was a problem while opening/reading the file '%(path_to_file)s'"
	CANNOT_CREATE_DIRECTORY	= "There was a problem while creating the directory '%(directory)s'"
	INVALID_XML_FILE	= "'%(path_to_xml)s' is an invalid XML file"
	XML_TAG_MISSING		= "'%(xml_tag_name)s' tag is missing in the XML configuration file '%(path_to_xml)s'"
	EMPTY_XML_TAG_ATTR	= "The tag attribute '%(xml_tag_attr)s' cannot be empty in '%(path_to_xml)s'"
	EMPTY_XML_TAG_VALUE	= "The tag '%(xml_tag_name)s' cannot be empty in '%(path_to_xml)s'"
	INVALID_IDENTIFIER	= "'%(identifier)s' is an invalid identifier ('%(path_to_xml)s')"
	INVALID_DEBUG_VALUE	= "'%(value)s' is an invalid debug value in '%(path_to_xml)s', defaulted to 'true'"

	"""Log's subdirectories constants"""

	INTERNAL = "internal"
	SCRAPER = "scraper"

	config = {
		"path_to_config" : dirname(dirname(dirname(abspath(__file__)))) + "/config/messages.xml",
		"debug" : True
	}

	true_list = ["true", "yes", "y", "1"]

	false_list = ["false", "no", "n", "0"]

	log = Log()

	validation = Validation()
	
	def __init__(self, debug_force_messages_content = None, debug_force_messages_path = None):

		try:

			if debug_force_messages_content:

				dom = minidom.parseString(debug_force_messages_content)

			else:

				if debug_force_messages_path:

					dom = minidom.parse(debug_force_messages_path)

				else:

					dom = minidom.parse(self.config["path_to_config"])

		except IOError:

			self.raise_error(self.XML_CONFIG_IO_ERROR % {
				"path_to_xml" : self.config["path_to_config"]
			}, self.INTERNAL)

		except ExpatError:

			self.raise_error(self.INVALID_XML_FILE % {
				"path_to_xml" : self.config["path_to_config"]
			}, self.INTERNAL)

		try:

			root = dom.getElementsByTagName("messages")[0]

		except IndexError:

			self.raise_error(self.XML_TAG_MISSING % {
				"xml_tag_name" : "messages",
				"path_to_xml" : self.config["path_to_config"]
			}, self.INTERNAL)

		debug = root.getElementsByTagName("debug")

		messages = root.getElementsByTagName("message")

		# We 'poke' the variable debug[0] to see if there is a 'debug' tag defined in the XML configuration file

		try:

			debug[0]

		except IndexError:

			# The tag 'debug' is missing, program halted

			self.raise_error(self.XML_TAG_MISSING % {
				"xml_tag_name" : "debug",
				"path_to_xml" : self.config["path_to_config"]
			}, self.INTERNAL)

		# We verify that the 'debug' tag content exists and is not an empty (whitespace) string

		if not debug[0].firstChild or not debug[0].firstChild.nodeValue.strip():

			# 'debug' tag content doesn't exists (empty) or is an empty string (whitespace)
			# We default to True and issue a warning

			self.issue_warning(self.INVALID_DEBUG_VALUE % {
				"value" : "",
				"path_to_xml" : self.config["path_to_config"]
			}, self.INTERNAL)

		else:

			debug = debug[0].firstChild.nodeValue.strip().lower()

			if debug in self.true_list:

				self.config["debug"] = True

			elif debug in self.false_list:

				self.config["debug"] = False

			else:

				# The content of the tag 'debug' is invalid (!= [true | false])
				# We default to True and issue a warning

				self.issue_warning(self.INVALID_DEBUG_VALUE % {
					"value" : debug,
					"path_to_xml" : self.config["path_to_config"]
				}, self.INTERNAL)

		# We 'poke' the variable messages[0] to see if there is a 'message' tag defined in the XML configuration file

		try:

			messages[0]

		except IndexError:

			self.raise_error(self.XML_TAG_MISSING % {
				"xml_tag_name" : "message",
				"path_to_xml" : self.config["path_to_config"]
			}, self.INTERNAL)

		for message in messages:

			message_name = message.getAttribute("name").strip().upper()

			if not message_name:

				self.raise_error(self.EMPTY_XML_TAG_ATTR % {
					"xml_tag_attr" : "message['name']",
					"path_to_xml" : self.config["path_to_config"]
				}, self.INTERNAL)

			if not self.validation.validate_identifier(message_name):

				self.raise_error(self.INVALID_IDENTIFIER % {
					"identifier" : "message['" + message_name + "']",
					"path_to_xml" : self.config["path_to_config"]
				}, self.INTERNAL)

			if not message.firstChild or not message.firstChild.nodeValue.strip():

				self.raise_error(self.EMPTY_XML_TAG_VALUE % {
					"xml_tag_name" : "message['" + message_name + "']",
					"path_to_xml" : self.config["path_to_config"]
				}, self.INTERNAL)

			vars(self)[message_name] = message.firstChild.nodeValue.strip(whitespace + ".")

	def __del__(self):

		# [Low] TODO

		pass

	def raise_error(self, message, section = SCRAPER, log_it = True):

		message = "Error: " + message + ".\n"

		if self.config["debug"]:

			stderr.write(message)

		if log_it:

			try:

				self.log.log_this(message, section)

			except IOError:

				self.issue_warning(self.GENERIC_FILE_IO_ERROR % {
					"path_to_file" : self.log.current_path_to_log
				}, self.INTERNAL)

			except OSError:

				self.issue_warning(self.CANNOT_CREATE_DIRECTORY % {
					"directory" : self.log.current_path_to_log
				}, self.INTERNAL)

		exit(1)

	def issue_warning(self, message, section = SCRAPER, log_it = True):

		message = "Warning: " + message + ".\n"

		if self.config["debug"]:

			stderr.write(message)

		if log_it:

			try:

				self.log.log_this(message, section)

			except:

				pass

	def inform(self, message, new_line = True, section = SCRAPER, log_it = True):

		if new_line:

			message = message + ".\n"

		if self.config["debug"]:

			stdout.write(message)

		if log_it:

			try:

				self.log.log_this(message, section)

			except IOError:

				self.issue_warning(self.GENERIC_FILE_IO_ERROR % {
					"path_to_file" : self.log.current_path_to_log
				}, self.INTERNAL)

			except OSError:

				self.issue_warning(self.CANNOT_CREATE_DIRECTORY % {
					"directory" : self.log.current_path_to_log
				}, self.INTERNAL)
