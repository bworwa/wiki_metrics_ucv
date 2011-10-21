#User defined
from scraper import Scraper

scraper = Scraper()

scraper.run("http://en.wikipedia.org/w/index.php?title=Computer_science&limit=5000&action=history")

"""
$ time python main.py 

real	0m15.488s
user	0m0.044s
sys	0m0.008s

Succesful head request using pycurl.
"""

