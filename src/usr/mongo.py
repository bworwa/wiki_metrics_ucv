
# Native
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from os.path import abspath, dirname

# External
from pymongo import Connection
from pymongo.errors import AutoReconnect

# XCraper
from core.messages import Messages

class Mongo:

	config = {
		"path_to_config" : dirname(dirname(dirname(abspath(__file__)))) + "/config/mongo.xml",
		"host" : None,
		"port" : 0
	}

	messages = Messages()

	connection = None

	db = None

	def __init__(self):

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

		try:

			mongo = dom.getElementsByTagName("mongo")[0]

		except IndexError:

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "mongo",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		try:

			connection = mongo.getElementsByTagName("connection")[0]

		except IndexError:

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "connection",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		try:

			host = mongo.getElementsByTagName("host")[0]

		except IndexError:

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "host",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		if not host.firstChild or not host.firstChild.nodeValue.strip():

			self.messages.raise_error(self.messages.EMPTY_XML_TAG_VALUE % {
				"xml_tag_name" : "host",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		self.config["host"] = host.firstChild.nodeValue.strip().lower()

		try:

			port = mongo.getElementsByTagName("port")[0]

		except IndexError:

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "port",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		if not port.firstChild or not port.firstChild.nodeValue.strip():

			self.messages.raise_error(self.messages.EMPTY_XML_TAG_VALUE % {
				"xml_tag_name" : "port",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		try:

			self.config["port"] = int(port.firstChild.nodeValue.strip())

		except ValueError:

			self.messages.raise_error(self.messages.INVALID_PORT % {
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		try:		

			self.connection = Connection(self.config["host"], self.config["port"])

		except AutoReconnect as message:

			self.messages.raise_error("PyMongo " + message.__str__(), self.messages.INTERNAL)

		try:

			database = mongo.getElementsByTagName("database")[0]

		except IndexError:

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "database",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		if not database.firstChild or not database.firstChild.nodeValue.strip():

			self.messages.raise_error(self.messages.EMPTY_XML_TAG_VALUE % {
				"xml_tag_name" : "database",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		self.db = self.connection[database.firstChild.nodeValue.strip().lower()]

	def __del__(self):

		# [Low] TODO

		pass

	def insert_new_article(self, url, priority = 0.5, last_update = 0):

		self.db.articles.insert({ "_id" : url, "priority" : priority, "last_update" : last_update })

	def remove_article(self, url):

		self.db.articles.remove({ "_id" : url })

	def remove_histories_by_article(self, article_url):

		self.db.histories.remove({ "article" : article_url })

	def update_article_url(self, old_url, new_url):

		article = self.db.articles.find({ "_id" : old_url })

		if article.count() == 1:

			self.insert_new_article(new_url, article[0]["priority"], article[0]["last_update"])

			self.db.histories.update({ "article" : old_url }, { "$set" : { "article" : new_url } } )

			self.remove_article(old_url)

		else:

			self.insert_new_article(new_url)

	def get_next_article(self):

		article = self.db.articles.find({}, { "_id" : 1, "last_update" : 1 }).sort("priority", -1).limit(1)

		if article.count(True) == 1:

			return { "url" : article[0]["_id"], "last_update" : article[0]["last_update"] }

		else:

			return None		

	def get_last_revision(self, url):

		revision = self.db.histories.find({ "article" : url }, { "_id" : 1 }).sort("_id", -1).limit(1)

		if revision.count(True) == 1:

			return { "mediawiki_id" : revision[0]["_id"] }

		else:

			return None

	def insert_revision(self, revision):

		self.db.histories.insert(revision)
