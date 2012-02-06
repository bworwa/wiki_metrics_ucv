
# Native
from os import makedirs, remove
from os.path import abspath, dirname, exists

class Control_Files:

	def file_exists(self, file_path):

		try:

			open(file_path)

		except IOError:

			return False

		return True

	def create_file(self, file_path, content = ""):

		if not exists(dirname(file_path)):

			try:

				makedirs(dirname(file_path))

			except OSError, error:

				# [Medium] TODO

				pass

		try:

			_file = open(file_path, 'w')

			_file.write(str(content))

			_file.close()

		except IOError:

			# [Medium] TODO

			pass

	def get_content(self, file_path):

		try:

			_file = open(file_path, 'r')

			content = _file.read().strip()

			_file.close()

			if content:

				return content

		except IOError:

			# [Medium] TODO

			pass

		return None

	def remove_file(self, file_path):

		try:

			remove(file_path)

		except OSError:

			# [Medium] TODO

			pass
