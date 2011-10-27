
# Native

from urlparse import parse_qs

# User defined

from core.scraper import Scraper

"""Example of a multi-page history traverse"""

host = "http://en.wikipedia.org"
rest = "/w/index.php?title=Du%C8%99mani&action=history&limit=4"

while True:

	scraper = Scraper()

	print "Visiting " + host + rest

	scraper.run(host + rest, "1319302255")

	try:

		rest = scraper.next_page[0].nodeValue

	except IndexError:

		print "Done"

		break
