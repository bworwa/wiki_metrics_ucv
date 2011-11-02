
# User defined

from core.scraper import Scraper

url = "http://es.wikipedia.org/w/index.php?title=Wikipedia:Portada&action=history"

scraper = Scraper()

print scraper.run(url)
