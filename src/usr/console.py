
# Native
from os import system
from sys import stdout

# User defined
from usr.threads import Threads
from usr.urls import Urls

class Console:

	COMMANDS = """Allowed commands:

General commands:

    clear:			clears the screen.
    exit:			stops all threads and halts the execution.
    start -[ a | p | w ]:	starts the specified thread(s).
    stop -[ a | p | w ]:	stops the specified thread(s).
    tstatus:			shows all threads status.
    url -[ add | rm ] [ URL ]:	adds or removes the specified URL(s).
"""

	START_OPTIONS = """Allowed options:

General Options:

    a:	starts all the threads.
    p:	starts the priority thread.
    w:	starts the wikimetrics thread.
"""

	STOP_OPTIONS = """Allowed options:

General Options:

    a:	stops all the threads.
    p:	stops the priority thread.
    w:	stops the wikimetrics thread.
"""

	URL_OPTIONS = """Allowed options:

General Options:

    -add:	adds the specified URL(s).
    -rm:	removes the specified URL(s).

Input Options:

    URL:		a valid HTTP/HTTPS/SHTTP URL.
    -f file.ext:	a file containing a set of 'URL', one per line.
"""

	status = "stopped"

	threads = Threads()

	urls = Urls()

	def __init__(self):

		self.status = "running"

		pass

	def __del__(self):

		# [Low] TODO

		pass

	def run(self):

		command = raw_input(">>> ")

		command_list = command.split()

		try:

			if command_list[0] == "clear":

				system("clear")

			elif command_list[0] == "exit":

				self.threads.stop_all_threads()

				self.status = "stopped"

				stdout.write("Bye!\n")

			elif command_list[0] == "start":

				try:

					if "-a" in command_list[1]:

						self.threads.start_all_threads()

					elif "-p" in command_list[1]:

						self.threads.start_priority_thread()

					elif "-w" in command_list[1]:

						self.threads.start_wikimetrics_thread()

					else:

						raise IndexError

				except IndexError:

					stdout.write(self.START_OPTIONS)

			elif command_list[0] == "stop":

				try:

					if command_list[1] == "-a":

						self.threads.stop_all_threads()

					elif command_list[1] == "-p":

						self.threads.stop_priority_thread()

					elif command_list[1] == "-w":

						self.threads.stop_wikimetrics_thread()

					else:

						raise IndexError

				except IndexError:

					stdout.write(self.STOP_OPTIONS)

			elif command_list[0] == "tstatus":

				stdout.write("Priority thread: " + self.threads.priority_thread["status"] + ".\n")

				stdout.write("Wikimetrics thread: " + self.threads.wikimetrics_thread["status"] + ".\n")

			elif command_list[0] == "url":

				try:

					if command_list[1] == "-add":

						try:

							if command_list[2] == "-f":

								self.urls.add_url(None, command_list[3])

							else:

								self.urls.add_url(command_list[2])

						except IndexError:

							raise IndexError

					elif command_list[1] == "-rm":

						pass

					else:

						raise IndexError

				except IndexError:

					stdout.write(self.URL_OPTIONS)

			else:

				stdout.write(self.COMMANDS)

		except IndexError:

			pass
