
# Native
from threading import Thread
from time import sleep
from sys import stdout

# User defined
from usr.wikimetrics import Wikimetrics, ResolvePendingFailed
from usr.mongo import Mongo
from usr.priority import Priority

class Threads:

	priority_thread = {
		"group" : None,
		"name" : "wiki_metrics_ucv_priority_thread",
		"callback" : None,
		"status" : "stopped",
		"thread" : None
	}

	wikimetrics_thread = {
		"group" : None,
		"name" : "wiki_metrics_ucv_wikimetrics_thread",
		"callback" : None,
		"status" : "stopped",
		"thread" : None
	}

	priority = Priority()

	mongo = Mongo()

	wikimetrics = Wikimetrics()

	def __init__(self):

		self.start_all_threads()

	def __del__(self):

		# [Low] TODO

		pass

	def run_priority_thread(self):

		while self.priority_thread["status"] == "running":

			self.priority.run()

	def run_wikimetrics_thread(self):

		while self.wikimetrics_thread["status"] == "running":

			article = self.mongo.get_next_article()

			if article:

				try:

					self.wikimetrics.run(article["url"], article["last_update"])

				except ResolvePendingFailed:

					pass

			else:

				sleep(0.5)

	def instantiate_priority_thread(self):

		self.priority_thread["thread"] = Thread(
			self.priority_thread["group"],
			self.run_priority_thread,
			self.priority_thread["name"]
		)

	def instantiate_wikimetrics_thread(self):

		self.wikimetrics_thread["thread"] = Thread(
			self.wikimetrics_thread["group"],
			self.run_wikimetrics_thread,
			self.wikimetrics_thread["name"]
		)

	def stop_priority_thread(self, console_output = True):

		if console_output:

			stdout.write("Stopping priority thread... ")

			stdout.flush()

		self.priority_thread["status"] = "stopped"

		while self.priority_thread["thread"] and self.priority_thread["thread"].is_alive():

			sleep(0.5)

		self.priority_thread["thread"] = None

		if console_output:

			stdout.write("OK\n")

	def stop_wikimetrics_thread(self, console_output = True):

		if console_output:

			stdout.write("Stopping wikimetrics thread... ")

			stdout.flush()

		self.wikimetrics_thread["status"] = "stopped"

		while self.wikimetrics_thread["thread"] and self.wikimetrics_thread["thread"].is_alive():

			sleep(0.5)

		self.wikimetrics_thread["thread"] = None

		if console_output:

			stdout.write("OK\n")

	def stop_all_threads(self):

		self.stop_priority_thread()

		self.stop_wikimetrics_thread()

	def start_priority_thread(self):

		stdout.write("Starting priority thread... ")

		stdout.flush()

		if not self.priority_thread["status"] == "running":

			self.stop_priority_thread(False)

			self.instantiate_priority_thread()

			self.priority_thread["status"] = "running"

			self.priority_thread["thread"].start()

			stdout.write("OK\n")

		else:

			stdout.write("thread is already running\n")

	def start_wikimetrics_thread(self):

		stdout.write("Starting wikimetrics thread... ")

		stdout.flush()

		if not self.wikimetrics_thread["status"] == "running":

			self.stop_wikimetrics_thread(False)

			self.instantiate_wikimetrics_thread()

			self.wikimetrics_thread["status"] = "running"

			self.wikimetrics_thread["thread"].start()

			stdout.write("OK\n")

		else:

			stdout.write("thread is already running\n")

	def start_all_threads(self):

		self.start_priority_thread()

		self.start_wikimetrics_thread()
