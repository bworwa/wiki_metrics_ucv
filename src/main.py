
# Native
from threading import Thread
from sys import exit, stdout
from os import system
from getpass import getuser
from time import sleep

# User defined
from usr.wikimetrics import Wikimetrics, ResolvePendingFailed
from usr.mongo import Mongo
from usr.priority import Priority
from usr.urls import Urls

def run_priority_thread():

	while priority.status == "running":

		priority.run()

def run_wikimetrics_thread():

	while wikimetrics.status == "running":

		article = mongo.get_next_article()

		if article:

			try:

				wikimetrics.run(article["url"], article["last_update"])

			except ResolvePendingFailed:

				pass

		else:

			sleep(0.5)

def stop_all_threads():

	stdout.write("Stopping all threads... ")

	stdout.flush()

	priority.status = "stopped"

	priority_thread.join()

	wikimetrics.status = "stopped"

	wikimetrics_thread.join()

def stop_priority_thread():

	stdout.write("Stopping priority thread... ")

	stdout.flush()

	priority.status = "stopped"

	priority_thread.join()

def stop_wikimetrics_thread():

	stdout.write("Stopping wikimetrics thread... ")

	stdout.flush()

	wikimetrics.status = "stopped"

	wikimetrics_thread.join()

def run_console_thread():

	while True:

		command = raw_input(">>> ")

		command_list = command.split()

		try:

			if command_list[0] == "tstatus":

				stdout.write("Priority thread: " + priority.status + "\n")

				stdout.write("Wikimetrics thread: " + wikimetrics.status + "\n")

			elif command_list[0] == "stop":

				try:

					if "-a" in command_list[1]:

						stop_all_threads()

						stdout.write("OK\n")

					elif "-p" in command_list[1]:

						stop_priority_thread()

						stdout.write("OK\n")

					elif "-w" in command_list[1]:

						stop_wikimetrics_thread()

						stdout.write("OK\n")

					else:

						raise IndexError

				except IndexError:

					stdout.write(
					"Allowed options:\n\nGeneral Options:\n\ta:\tstops all the threads.\n\tp:\tstops the priority thread.\n\tw:\tstops the wikimetrics thread.\n"
					)

			elif command_list[0] == "start":

				global priority_thread, wikimetrics_thread

				try:

					if "-a" in command_list[1]:

						stdout.write("Starting all threads... ")

						priority.status = "running"

						wikimetrics.status = "running"

						if not priority_thread.is_alive():

							priority_thread = Thread(None, run_priority_thread, "wiki_metrics_ucv_priority_thread")

							priority_thread.start()

						if not wikimetrics_thread.is_alive():

							wikimetrics_thread = Thread(None, run_wikimetrics_thread, "wiki_metrics_ucv_wikimetrics_thread")

							wikimetrics_thread.start()

						stdout.write("OK\n")

					elif "-p" in command_list[1]:

						stdout.write("Starting priority thread... ")

						priority.status = "running"

						if not priority_thread.is_alive():

							priority_thread = Thread(None, run_priority_thread, "wiki_metrics_ucv_priority_thread")

							priority_thread.start()

						stdout.write("OK\n")

					elif "-w" in command_list[1]:

						stdout.write("Starting wikimetrics thread... ")

						wikimetrics.status = "running"

						if not wikimetrics_thread.is_alive():

							wikimetrics_thread = Thread(None, run_wikimetrics_thread, "wiki_metrics_ucv_wikimetrics_thread")

							wikimetrics_thread.start()

						stdout.write("OK\n")

					else:

						raise IndexError

				except IndexError:

					stdout.write(
					"Allowed options:\n\nGeneral Options:\n\ta:\tstarts all the threads.\n\tp:\tstarts the priority thread.\n\tw:\tstarts the wikimetrics thread.\n"
					)

			elif command_list[0] == "exit":

				stop_all_threads()

				stdout.write("OK\nBye!\n")

				break

			else:

				stdout.write(
					"Allowed commands:\n\nGeneral commands:\n\ttstatus:\t\tshows all threads status.\n\tstart -[ a | p | w ]:\tstarts the specified thread(s).\n\tstop -[ a | p | w ]:\tstops the specified thread(s).\n\texit:\t\t\tstops all threads and halts the execution.\n"
				)

		except IndexError:

			pass

if __name__ == "__main__":

	system("clear")

	priority = Priority()

	urls = Urls()

	mongo = Mongo()

	wikimetrics = Wikimetrics()

	priority.status = "running"

	wikimetrics.status = "running"

	priority_thread = Thread(None, run_priority_thread, "wiki_metrics_ucv_priority_thread")	

	wikimetrics_thread = Thread(None, run_wikimetrics_thread, "wiki_metrics_ucv_wikimetrics_thread")

	console_thread = Thread(None, run_console_thread, "wiki_metrics_ucv_console_thread")

	stdout.write("Starting the priority thread... ")

	priority_thread.start()

	stdout.write("OK\n")

	stdout.write("Starting the wikimetrics thread... ")

	wikimetrics_thread.start()

	stdout.write("OK\n")

	stdout.write("Starting the console thread... ")

	console_thread.start()

	stdout.write("OK\nWelcome " + getuser() + "!\n")
