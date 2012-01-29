
# Native
from sys import stdout

# User defined
from usr.mongo import Mongo
from usr.helpers.normalization import Normalization

class Urls:

	mongo = Mongo()

	normalization = Normalization()

	def __init__(self):

		# [Low] TODO

		pass

	def __del__(self):

		# [Low] TODO

		pass

	def add_url(self, url, path_to_file = None):

		if not path_to_file:

			normalized_url = self.normalization.normalize_article_to_history_url(url)

			if normalized_url:

				self.mongo.insert_new_article(normalized_url)

			else:

				stdout.write("URL '" + str(url) + "' is not a valid HTTP/HTTPS/SHTTP URL and will be ignored.\n")

		else:

			try:

				urls_file = open(path_to_file, "r")

				for url in urls_file:

					self.add_url(url.strip())

				urls_file.close()

			except IOError:

				stdout.write("There was a problem while opening/reading the file '" + str(path_to_file) + "'.\n")
