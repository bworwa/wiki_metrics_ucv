from datetime import date, datetime

path_to_log = "../logs/"

def log_this(message, internal = False):

	global path_to_log

	now = datetime.now()

	if internal:

		path_to_log += "internals/"

	path_to_log = (path_to_log + "%d-%d-%d.log") % (now.day, now.month, now.year)

	message = ("[%d:%d:%d] " + message) % (now.hour, now.minute, now.second)

	log = open(path_to_log, "a")

	log.write(message)

	log.close()

	del message, internal, path_to_log, now, log
