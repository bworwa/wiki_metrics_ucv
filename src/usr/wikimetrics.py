
# Native
from urlparse import urlparse, parse_qs
from time import strptime, mktime

# XCraper
from core.scraper import Scraper
from core.messages import Messages

# User defined
from usr.mongo import Mongo

class Wikimetrics:

	# TODO: Move to config

	revisions_limit = 20

	mongo = Mongo()

	scraper = Scraper()

	messages = Messages()

	def __init__(self):

		# [High] TODO

		pass

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
		}, True)

		response_code = self.scraper.run(url + "&limit=" + str(self.revisions_limit), last_update)

		if response_code:

			new_revisions_count = 0

			for index in range(len(self.scraper.revision)):

				mediawiki_id = int(parse_qs(self.scraper.mediawiki_id[index])["oldid"][0])

				if mediawiki_id and mediawiki_id > last_revision:

					revision = {
						"_id" : mediawiki_id,
						"article" : article_url,
						"date" : mktime(strptime(self.scraper.date[index], "%H:%M, %d %B %Y")),
						"user" : self.scraper.user[index],
						"minor" : True if self.scraper.minor[index] else False,
						"size" : int("".join(list(number for number in self.scraper.size[index] if number.isdigit()))),
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
				}, True)

			elif new_revisions_count == self.revisions_limit:

				if self.scraper.next_page[0]:

					self.messages.inform(self.messages.VISITING_NEXT_PAGE % {
						"quantity" : new_revisions_count,
						"url" : url
					}, True)

					parsed_url = urlparse(url)

					self.run(parsed_url[0] + "://" + parsed_url[1] + self.scraper.next_page[0], 0, last_revision, article_url)

				else:

					self.messages.inform(self.messages.NEW_REVISIONS_FOUND % {
						"quantity" : new_revisions_count,
						"url" : url
					}, True)

			else:

				self.messages.inform(self.messages.NEW_REVISIONS_FOUND % {
					"quantity" : new_revisions_count,
					"url" : url
				}, True)

		else:

			# [Medium] TODO: An error ocurred while doing the request

			pass
