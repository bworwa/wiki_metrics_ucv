
"""Core libraries, do not change"""

# Native
from datetime import date, datetime
from os.path import dirname, abspath, exists
from os import makedirs

class Log:

	BASE_PATH_TO_LOG = dirname(dirname(dirname(dirname(abspath(__file__))))) + "/logs"

	current_path_to_log = None

	def __init__(self):

		# [Low] TODO

		pass

	def __del__(self):

		# [Low] TODO

		pass

	def log_this(self, message, section):

		"""
			Logs the current [message] in the directory /logs/[section]/[current_date].log.
			If [section] does not exist it is automatically created
		"""

		self.current_path_to_log = self.BASE_PATH_TO_LOG + "/" + section

		if not exists(self.current_path_to_log):

			makedirs(self.current_path_to_log)

		now = datetime.now()

		self.current_path_to_log = (self.current_path_to_log + "/%d-%d-%d.log") % (now.day, now.month, now.year)

		message = ("[%d:%d:%d] " + message) % (now.hour, now.minute, now.second)

		log = open(self.current_path_to_log, "a")

		log.write(message)

		log.close()
