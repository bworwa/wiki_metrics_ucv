
# Native
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from os.path import abspath, dirname
from urlparse import urlparse, parse_qs
from time import strptime, mktime

# XCraper
from core.scraper import Scraper
from core.messages import Messages

# User defined
from usr.mongo import Mongo

class Wikimetrics:

	# TODO: Move to config

	config = {
		"path_to_config" : dirname(dirname(dirname(abspath(__file__)))) + "/config/wikimetrics.xml",
		"revisions_limit" : 0
	}

	mongo = Mongo()

	scraper = Scraper()

	messages = Messages()

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

			wikimetrics = dom.getElementsByTagName("wikimetrics")[0]

		except IndexError:

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "wikimetrics",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		try:

			revisions_limit = wikimetrics.getElementsByTagName("revisions_limit")[0]

		except IndexError:

			self.messages.raise_error(self.messages.XML_TAG_MISSING % {
				"xml_tag_name" : "revisions_limit",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		if not revisions_limit.firstChild or not revisions_limit.firstChild.nodeValue.strip():

			self.messages.raise_error(self.messages.EMPTY_XML_TAG_VALUE % {
				"xml_tag_name" : "revisions_limit",
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

		try:

			self.config["revisions_limit"] = int(revisions_limit.firstChild.nodeValue.strip())

		except ValueError:

			self.messages.raise_error(self.messages.INVALID_REVISIONS_LIMIT % {
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)
		
		if self.config["revisions_limit"] < 1:

			self.messages.raise_error(self.messages.INVALID_REVISIONS_LIMIT % {
				"path_to_xml" : self.config["path_to_config"]
			}, self.messages.INTERNAL)

	def __del__(self):

		# [Low] TODO

		pass

	def run(self, url, last_update, last_revision = None, article_url = None):

		if not last_revision:

			revision = self.mongo.get_last_revision(url)

			if revision:

				last_revision = revision["mediawiki_id"]

			else:

				last_revision = 0

		if not article_url:

			article_url = url

		self.messages.inform(self.messages.VISITING_URL % {
			"url" : url,
			"mediawiki_id" : last_revision
		})

		response_code = self.scraper.run(url + "&limit=" + str(self.config["revisions_limit"]), last_update)

		if response_code:

			if response_code == 200:

				# OK

				new_revisions_count = 0

				for index in range(len(self.scraper.revision)):

					if self.scraper.mediawiki_id[index]:

						mediawiki_id = int(parse_qs(self.scraper.mediawiki_id[index])["oldid"][0])

						if mediawiki_id > last_revision:

							size = "".join(list(number for number in self.scraper.size[index] if number.isdigit()))

							revision = {
								"_id" : mediawiki_id,
								"article" : article_url,
								"date" : mktime(strptime(self.scraper.date[index], "%H:%M, %d %B %Y")),
								"user" : self.scraper.user[index],
								"minor" : True if self.scraper.minor[index] else False,
								"size" :  int(size) if size else 0,
								"comment" : self.scraper.comment[index].replace("\n", "") if self.scraper.comment[index] else None
							}

							self.mongo.insert_revision(revision)

							new_revisions_count += 1

						else:

							break

				if new_revisions_count == 0:

					self.messages.inform(self.messages.NO_NEW_REVISIONS_FOUND % {
						"mediawiki_id" : last_revision,
						"url" : url
					})

				elif new_revisions_count == self.config["revisions_limit"]:

					if self.scraper.next_page[0]:

						self.messages.inform(self.messages.VISITING_NEXT_PAGE % {
							"quantity" : new_revisions_count,
							"url" : url
						})

						parsed_url = urlparse(url)

						self.run(parsed_url[0] + "://" + parsed_url[1] + self.scraper.next_page[0], 0, last_revision, article_url)

					else:

						self.messages.inform(self.messages.NEW_REVISIONS_FOUND % {
							"quantity" : new_revisions_count,
							"url" : url
						})

				else:

					self.messages.inform(self.messages.NEW_REVISIONS_FOUND % {
						"quantity" : new_revisions_count,
						"url" : url
					})

			elif response_code == 301:

				# Moved permanently

				parsed_url = urlparse(self.scraper.request.current_headers["location"], None, False)

				new_url = parsed_url[0] + "://" + parsed_url[1] + parsed_url[2] + parsed_url[3] + "?title=" + parse_qs(parsed_url[4])["title"][0] + "&action=history"

				self.mongo.update_article_url(article_url, new_url)				

				self.run(new_url, 0)

			elif response_code in [302, 303, 307]:

				# Found, See other

				parsed_url = urlparse(self.scraper.request.current_headers["location"], None, False)

				temporal_url = parsed_url[0] + "://" + parsed_url[1] + parsed_url[2] + parsed_url[3] + "?title=" + parse_qs(parsed_url[4])["title"][0] + "&action=history"

				self.run(temporal_url, 0, article_url)

			elif response_code == 408:

				# Timed out

				self.run(url, 0)

			elif response_code == 410:

				self.mongo.remove_article(article_url)

				self.mongo.remove_histories_by_article(article_url)

			else:

				self.messages.issue_warning(self.messages.CHECK_URL % {
					"url" : url
				})

		else:

			# [Medium] TODO: An error ocurred while doing the request

			pass
