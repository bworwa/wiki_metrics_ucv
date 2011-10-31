
"""Core libraries, do not change"""

#Native
from re import search, IGNORECASE
from urlparse import urlparse

class Validation:

	def __init__(self):

		# [Low] TODO

		pass

	def __del__(self):

		# [Low] TODO

		pass

	def validate_identifier(self, identifier):

		# According to http://docs.python.org/reference/lexical_analysis.html#identifiers

		match = search("^[a-z_][a-z0-9_]*", identifier, IGNORECASE)
	
		if match:

			return True

		return False

	def validate_url(self, url):

		# URLs must have the following format to be considered valid URLs
		# scheme://host[/path[?query][#fragment]]

		parsed_url = urlparse(url)

		if parsed_url[0] and (
			parsed_url[0] == "http" or parsed_url[0] == "https" or parsed_url[0] == "shttp"
		) and parsed_url[1]:

			# That's enough to be considered a valid URL

			return True

		return False
