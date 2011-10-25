#User defined
from scraper import Scraper

scraper = Scraper()

scraper.run("http://en.wikipedia.org/w/index.php?title=Computer_science&limit=2&action=history", "1319302255")
