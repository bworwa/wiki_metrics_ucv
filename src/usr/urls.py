
# XCraper
from core.messages import Messages

# User defined
from usr.mongo import Mongo
from usr.helpers.normalization import Normalization

class Urls:

	messages = Messages()

	mongo = Mongo()

	normalization = Normalization()

	def __init__(self):

		self.messages.URLS = "urls"

		pass

	def __del__(self):

		# [Low] TODO

		pass

	def add_url(self, url, path_to_file = None):

		if not path_to_file:

			normalized_url = self.normalization.normalize_article_to_history_url(url)

			if normalized_url:

				print normalized_url

			else:

				self.messages.issue_warning(self.messages.INVALID_URL % {
					"url" : url
				}, self.messages.URLS)

		else:

			try:

				urls_file = open(path_to_file, "r")

			except IOError:

				self.messages.raise_error(self.messages.GENERIC_FILE_IO_ERROR % {
					"path_to_file" : path_to_file
				}, self.messages.URLS)

			for url in urls_file:

				self.add_url(url.strip())

			urls_file.close()
