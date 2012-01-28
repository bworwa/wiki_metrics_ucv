
# Native
from sys import stdout

# User defined
from usr.threads import Threads

class Console:

	STOP_OPTIONS = """Allowed options:

General Options:

	a:	stops all the threads.
	p:	stops the priority thread.
	w:	stops the wikimetrics thread.
"""

	START_OPTIONS = """Allowed options:

General Options:

	a:	starts all the threads.
	p:	starts the priority thread.
	w:	starts the wikimetrics thread.
"""

	COMMANDS = """Allowed commands:

General commands:
	
	tstatus:		shows all threads status.
	start -[ a | p | w ]:	starts the specified thread(s).
	stop -[ a | p | w ]:	stops the specified thread(s).
	exit:			stops all threads and halts the execution.
"""

	status = "stopped"

	threads = Threads()

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

			if command_list[0] == "tstatus":

				stdout.write("Priority thread: " + self.threads.priority_thread["status"] + "\n")

				stdout.write("Wikimetrics thread: " + self.threads.wikimetrics_thread["status"] + "\n")

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

			elif command_list[0] == "exit":

				self.threads.stop_all_threads()

				self.status = "stopped"

				stdout.write("Bye!\n")

			else:

				stdout.write(self.COMMANDS)

		except IndexError:

			pass
