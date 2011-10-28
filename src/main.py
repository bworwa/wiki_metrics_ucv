
# Native

from urlparse import parse_qs

# User defined

from core.scraper import Scraper

"""Example of a multi-page history traverse"""

host = "http://en.wikipedia.org"
rest = "/w/index.php?title=Du%C8%99mani&action=history&limit=4"

scraper = Scraper()

while True:


	scraper.run(host + rest, "1319302255")

	for i in range(len(scraper.revision)):

		print scraper.mediawiki_id[i].nodeValue
		print scraper.date[i]
		print scraper.user[i]
		print scraper.minor[i]
		print scraper.size[i]
		print scraper.comment[i]

	try:

		rest = scraper.next_page[0].nodeValue

	except IndexError:

		print "Done"

		break
