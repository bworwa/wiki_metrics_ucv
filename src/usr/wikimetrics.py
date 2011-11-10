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

	def get_next_article(self):

		article = self.mongo.db.articles.find({}, { "_id" : 1, "last_update" : 1 }).sort("priority", -1).limit(1)

		if article.count(True) == 1:

			return { "url" : article[0]["_id"], "last_update" : article[0]["last_update"] }

		else:

			return None

	def get_last_revision(self, url):

		revision = self.mongo.db.histories.find({ "article" : url }, { "_id" : 1 }).sort("_id", -1).limit(1)

		if revision.count(True) == 1:

			return { "mediawiki_id" : revision[0]["_id"] }

		else:

			return None

	def insert_revision(self, revision):

		self.mongo.db.histories.insert(revision)

	def run(self, url, last_update):

		revision = self.get_last_revision(url)

		if revision:

			last_revision = revision["mediawiki_id"]

		else:

			last_revision = 0

		# TODO: move to function 'inform' in core.messages

		print self.messages.VISITING_URL % {
			"url" : url,
			"mediawiki_id" : last_revision
		}

		response_code = self.scraper.run(url + "&limit=" + str(self.revisions_limit), last_update)

		if response_code:

			new_revisions_count = 0

			for index in range(len(self.scraper.revision)):

				mediawiki_id = int(parse_qs(self.scraper.mediawiki_id[index])["oldid"][0])

				if mediawiki_id and mediawiki_id > last_revision:

					revision = {
						"_id" : mediawiki_id,
						"article" : url,
						"date" : mktime(strptime(self.scraper.date[index], "%H:%M, %d %B %Y")),
						"user" : self.scraper.user[index],
						"minor" : True if self.scraper.minor[index] else False,
						"size" : int("".join(list(number for number in self.scraper.size[index] if number.isdigit()))),
						"comment" : self.scraper.comment[index].replace("\n", "") if self.scraper.comment[index] else None
					}

					self.insert_revision(revision)

					new_revisions_count += 1

			if new_revisions_count == 0:

				print "No further revisions found."

			elif new_revisions_count == self.revisions_limit:

				try:

					print "We need to visit the next page."

					self.scraper.next_page

				except AttributeError:

					pass
