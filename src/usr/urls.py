
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

		total_urls = 0

		urls_added = 0

		if not path_to_file:

			total_urls = 1

			normalized_url = self.normalization.normalize_article_to_history_url(url)

			if normalized_url:

				self.mongo.insert_new_article(normalized_url)

				urls_added += 1

				self.messages.inform(self.messages.URL_ADDED % {
					"url" : normalized_url
				}, True, self.messages.URLS)

			else:

				self.messages.issue_warning(self.messages.INVALID_URL % {
					"url" : url
				}, self.messages.URLS)

		else:

			try:

				urls_file = open(path_to_file, "r")

				for url in urls_file:

					total_urls += 1

					urls_added += self.add_url(url.strip())[0]

				urls_file.close()

			except IOError:

				self.messages.issue_warning(self.messages.GENERIC_FILE_IO_ERROR % {
					"path_to_file" : path_to_file
				}, self.messages.URLS)

		return (urls_added, total_urls)

	def remove_url(self, url, path_to_file = None):

		total_urls = 0

		urls_removed = 0

		if not path_to_file:

			total_urls = 1

			normalized_url = self.normalization.normalize_article_to_history_url(url)

			if normalized_url:

				self.mongo.remove_article(normalized_url)

				self.mongo.remove_histories_by_article(normalized_url)

				urls_removed += 1

				self.messages.inform(self.messages.URL_REMOVED % {
					"url" : normalized_url
				}, True, self.messages.URLS)

			else:

				self.messages.issue_warning(self.messages.INVALID_URL % {
					"url" : url
				}, self.messages.URLS)

		else:

			try:

				urls_file = open(path_to_file, "r")

				for url in urls_file:

					total_urls += 1

					urls_removed += self.remove_url(url.strip())[0]

				urls_file.close()

			except IOError:

				self.messages.issue_warning(self.messages.GENERIC_FILE_IO_ERROR % {
					"path_to_file" : path_to_file
				}, self.messages.URLS)

		return (urls_removed, total_urls)
