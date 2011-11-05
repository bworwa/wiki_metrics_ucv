
# Native

from urlparse import parse_qs
from time import strptime, mktime

# XCraper

from core.scraper import Scraper

# User defined

from usr.mongo import Mongo

scraper = Scraper()

mongo = Mongo()

revisions_limit = "20"

article = mongo.db.articles.find().sort("priority", -1).limit(1)

if article:

	try:

		response_code = scraper.run(article[0]["_id"] + "&limit=" + revisions_limit, article[0]["last_update"])

		for index in range(len(scraper.revision)):

			mediawiki_id = int(parse_qs(scraper.mediawiki_id[index])["oldid"][0])

			if mediawiki_id:

				revision = {
					"_id" : mediawiki_id,
					"article" : article[0]["_id"],
					"date" : mktime(strptime(scraper.date[index], "%H:%M, %d %B %Y")),
					"user" : scraper.user[index],
					"minor" : True if scraper.minor[index] else False,
					"size" : int("".join(list(number for number in scraper.size[index] if number.isdigit()))),
					"comment" : scraper.comment[index].replace("\n", "") if scraper.comment[index] else None
				}

				mongo.db.histories.insert(revision)

	except IndexError:

		print "No URLs found, collection 'articles' is empty."

	except AttributeError:

		# Exception raised when 'scraper.run()' returns False and, therefore, no query variables were defined

		pass
