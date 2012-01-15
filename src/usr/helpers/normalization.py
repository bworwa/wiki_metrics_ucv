
#Native
from urlparse import urlparse, parse_qs

class Normalization:

	def __init__(self):

		# [Low] TODO

		pass

	def __del__(self):

		# [Low] TODO

		pass

	def normalize_mediawiki_url(self, url):

		parsed_url = urlparse(url, None, False)

		scheme = parsed_url[0]

		host = parsed_url[1]

		path = parsed_url[2]

		path_parameters = parsed_url[3]

		query_string = parse_qs(parsed_url[4])

		url = scheme + "://" + host + path

		if path_parameters:

			url += ";" + path_parameters

		if query_string:

			url += "?title=" + query_string["title"][0] + "&action=history"

			try:

				url += "&offset=" + query_string["offset"][0]

			except KeyError:

				pass

		return url
