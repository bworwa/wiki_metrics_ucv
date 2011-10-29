
# Native

from urlparse import parse_qs

# User defined

from core.scraper import Scraper

url = "http://en.wikipedia.org/w/index.php?title=Vaf%C3%BEr%C3%BA%C3%B0nir&action=history"

scraper = Scraper()

scraper.run(url, 0)

print "Done"
