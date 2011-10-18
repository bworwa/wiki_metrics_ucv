from datetime import date, datetime
from os import path, makedirs

#Careful with this, otherwise you'll create backup directories all over the place
current_path_to_log = "../logs"

def log_this(message, section):

	"""Logs the current [message] in the directory /logs/[section]/[current_date].log. If [section] does not exist it is automatically created"""

	global current_path_to_log

	current_path_to_log = current_path_to_log + "/" + section

	if not path.exists(current_path_to_log):

		makedirs(current_path_to_log)

	now = datetime.now()

	current_path_to_log = (current_path_to_log + "/%d-%d-%d.log") % (now.day, now.month, now.year)

	message = ("[%d:%d:%d] " + message) % (now.hour, now.minute, now.second)

	log = open(current_path_to_log, "a")

	log.write(message)

	log.close()

	del message, section, current_path_to_log, now, log
