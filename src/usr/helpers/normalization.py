
# Native
from urlparse import urlparse, parse_qs

# User defined
from core.helpers.validation import Validation

class Normalization:

	validation = Validation()

	def __init__(self):

		# [Low] TODO

		pass

	def __del__(self):

		# [Low] TODO

		pass

	def normalize_mediawiki_url(self, url):

		if url:

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

				try:

					url += "?title=" + query_string["title"][0] + "&action=history"

					url += "&offset=" + query_string["offset"][0]

				except KeyError:

					pass

			return url

		return None

	def normalize_article_to_history_url(self, url):

		if url:

			if self.validation.validate_url(url):

				parsed_url = urlparse(url, None, False)

				scheme = parsed_url[0]

				host = parsed_url[1]

				path = parsed_url[2]

				path_parameters = parsed_url[3]

				query_string = parse_qs(parsed_url[4])

				if query_string and query_string["title"][0]:

					url = self.normalize_mediawiki_url(url)

				else:

					# Only for Wikipedia

					url = scheme + "://" + host + "/w/index.php?title=" + path.replace("/wiki/", "").strip() + "&action=history"

				return url

		return None
