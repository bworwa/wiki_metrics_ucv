
# Native
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from os.path import abspath, dirname
from urlparse import urlparse, parse_qs
from time import strptime, mktime, sleep, time
from locale import LC_TIME, getlocale, setlocale
import md5

# XCraper
from core.scraper import Scraper
from core.messages import Messages

# External
from pymongo.errors import DuplicateKeyError

# User defined
from usr.mongo import Mongo
from usr.helpers.normalization import Normalization

class ResolvePendingFailed(Exception):

	pass

class Wikimetrics:

	# TODO: Move to config

	config = {
		"path_to_config" : dirname(dirname(dirname(abspath(__file__)))) + "/config/wiki_metrics.xml",
		"revisions_limit" : 0
	}

	mongo = Mongo()

	scraper = Scraper()

	messages = Messages()

	normalization = Normalization()

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

	def run(self, url, last_update, last_revision = None, article_url = None, tries = 0, is_page = False):

		if not article_url:

			pending_url = self.mongo.get_pending_url(url)

			if pending_url and pending_url != url:

				self.run(pending_url, 0, 0, url, 0, True)

				if self.mongo.get_pending_url(url):

					raise ResolvePendingFailed()

		if last_revision is None:

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

				history_md5 = md5.new(self.scraper.history[0]).hexdigest()

				if history_md5 == self.mongo.get_last_history_md5(article_url):

					self.messages.inform(self.messages.NO_NEW_REVISIONS_FOUND % {
						"mediawiki_id" : last_revision,
						"url" : url
					})

				else:

					new_revisions_count = 0

					for index in range(len(self.scraper.revision)):

						if self.scraper.mediawiki_id[index]:

							mediawiki_id = int(parse_qs(self.scraper.mediawiki_id[index])["oldid"][0])

							if mediawiki_id > last_revision:

								size = "".join(list(number for number in self.scraper.size[index] if number.isdigit()))

								try:

									date = mktime(strptime(self.scraper.date[index], "%H:%M, %d %B %Y"))

								except ValueError:

									# Spanish Wikipedia fix
									# Locales taken from bash$ locale -a
									# These are OS dependant

									setlocale(LC_TIME, "es_ES.utf8")

									date = mktime(strptime(self.scraper.date[index], "%H:%M %d %b %Y"))

									setlocale(LC_TIME, "en_US.utf8")

								revision = {
									"_id" : mediawiki_id,
									"article" : article_url,
									"date" : date,
									"user" : self.scraper.user[index],
									"minor" : True if self.scraper.minor[index] else False,
									"size" :  int(size) if size else 0,
									"comment" : self.scraper.comment[index].replace("\n", "") if self.scraper.comment[index] else None
								}

								try:

									self.mongo.insert_revision(revision)

									new_revisions_count += 1

								except DuplicateKeyError:

									break

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

							parsed_article_url = urlparse(article_url)

							next_page_url = self.normalization.normalize_mediawiki_url(
								parsed_article_url[0] + "://" + parsed_article_url[1] + self.scraper.next_page[0]
							)

							self.run(next_page_url, 0, last_revision, article_url, 0, True)

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

					if not is_page:

						if not self.mongo.get_pending_url(article_url):

							self.mongo.update_article_pending_url(article_url, None)

						self.mongo.update_last_history_md5(article_url, history_md5)

			elif response_code == 301:

				# Moved permanently

				new_url = self.normalization.normalize_mediawiki_url(self.scraper.request.current_headers["location"])

				self.mongo.update_article_url(article_url, new_url)				

				self.run(new_url, last_update, last_revision, None, tries, is_page)

			elif response_code in [302, 303, 307]:

				# Found, See other

				temporal_url = self.normalization.normalize_mediawiki_url(self.scraper.request.current_headers["location"])

				self.run(temporal_url, last_update, last_revision, article_url, tries, is_page)

			elif response_code in [408, 500, 503]:

				if tries < 3:

					try:

						sleep(self.scraper.request.current_headers["retry-after"] - self.scraper.request.crawl_delay)

					except KeyError:

						pass

					except TypeError:

						pass

					self.run(url, last_update, last_revision, article_url, tries + 1, is_page)

				else:

					self.mongo.update_article_pending_url(article_url, url)

					self.messages.issue_warning(self.messages.CHECK_URL % {
						"url" : url
					})

					self.messages.inform(self.messages.PENDING_URL % {
						"pending_url" : url,
						"article" : article_url
					})

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

		if not is_page:

			self.mongo.update_article_last_update(article_url, int(time()) + 16200) # Wikipedia uses GMT

			self.mongo.update_article_priority(article_url, 0)
