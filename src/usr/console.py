
# Native
from os import system
import readline

# XCraper
from core.messages import Messages

# User defined
from usr.threads import Threads
from usr.urls import Urls

class Console:

	status = "stopped"

	messages = Messages()

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

				self.messages.inform(self.messages.CONSOLE_BYE, True, None, False)

			elif command_list[0] == "start":

				try:

					if command_list[1] == "-a":

						self.threads.start_all_threads()

					elif command_list[1] == "-p":

						self.threads.start_priority_thread()

					elif command_list[1] == "-w":

						self.threads.start_wikimetrics_thread()

					else:

						raise IndexError

				except IndexError:

					self.messages.inform(self.messages.CONSOLE_START_OPTIONS, True, None, False)

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

					self.messages.inform(self.messages.CONSOLE_STOP_OPTIONS, True, None, False)

			elif command_list[0] == "tstatus":

				self.threads.inform_threads_status()

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

						try:

							if command_list[2] == "-f":

								self.urls.remove_url(None, command_list[3])

							else:

								self.urls.remove_url(command_list[2])

						except IndexError:

							raise IndexError

					else:

						raise IndexError

				except IndexError:

					self.messages.inform(self.messages.CONSOLE_URL_OPTIONS, True, None, False)

			else:

				self.messages.inform(self.messages.CONSOLE_COMMANDS, True, None, False)

		except IndexError:

			pass
