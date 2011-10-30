
# Native

from urlparse import parse_qs

# User defined

from core.scraper import Scraper

url = "http://en.wikipedia.org/w/index.php?title=Du%C8%99mani&action=history&limit=4"

scraper = Scraper()

print scraper.run(url)
