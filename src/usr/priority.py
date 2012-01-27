
# Native
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from os.path import abspath, dirname
from time import sleep

# XCraper
from core.messages import Messages

# User defined
from usr.mongo import Mongo

class Priority:

	config = {
		"path_to_config" : dirname(dirname(dirname(abspath(__file__)))) + "/config/priority.xml",
		"time_to_sleep" : 0
	}

	messages = Messages()

	mongo = Mongo()

	def __init__(self, debug_force_config_content = None, debug_force_config_path = None):

		try:

			if debug_force_config_content:

				dom = minidom.parseString(debug_force_config_content)

			else:

				if debug_force_config_path:

					dom = minidom.parse(debug_force_config_path)				

				else:

					dom = minidom.parse(self.config["path_to_config"])

		except IOError:

			self.messages.raise_error(self.messages.XML_CONFIG_IO_ERROR % {
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		except ExpatError:

			self.messages.raise_error(self.messages.INVALID_XML_FILE % {
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		try:

			priority = dom.getElementsByTagName("priority")[0]

		except IndexError:

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "priority",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		try:

			time_to_sleep = priority.getElementsByTagName("time_to_sleep")[0]

		except IndexError:

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "time_to_sleep",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)


		if not time_to_sleep.firstChild or not time_to_sleep.firstChild.nodeValue.strip():

			self.messages.raise_error(self.messages.EMPTY_XML_TAG_VALUE % {
				"xml_tag_name" : "time_to_sleep",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		try:

			self.config["time_to_sleep"] = int(time_to_sleep.firstChild.nodeValue.strip())

		except ValueError:

			self.messages.raise_error(self.messages.INVALID_TIME_TO_SLEEP % {
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		if self.config["time_to_sleep"] < 1:

			self.messages.raise_error(self.messages.INVALID_TIME_TO_SLEEP % {
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

	def __del__(self):

		# [Low] TODO

		pass

	def run(self):

		self.mongo.batch_update_articles_priority()

		sleep(self.config["time_to_sleep"])
