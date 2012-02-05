
# Native
from os import makedirs, remove, system
from os.path import abspath, dirname, exists
from signal import signal, SIGTERM
import readline

# XCraper
from core.messages import Messages

# User defined
from usr.threads import Threads
from usr.urls import Urls
from usr.daemon import Daemon, Priority_Daemon, Wikimetrics_Daemon

class Console:

	config = {
		"lock_file_path" : dirname(dirname(dirname(abspath(__file__)))) + "/tmp/console.lock"
	}

	status = "stopped"

	messages = Messages()

	threads = Threads()

	urls = Urls()

	def __init__(self):

		self.status = "running"

		# Create/write .lock file

		if not exists(dirname(self.config["lock_file_path"])):

			try:

				makedirs(dirname(self.config["lock_file_path"]))

			except OSError:

				# [Medium] TODO

				pass

		try:

			file(self.config["lock_file_path"], 'w').write("")

		except OSError:

			# [Medium] TODO

			pass

		signal(SIGTERM, self.sigterm_handler)

	def __del__(self):

		# [Low] TODO

		pass

	def sigterm_handler(self, signal_number, frame):

		self.threads.stop_all_threads()

		try:

			remove(self.config["lock_file_path"])

		except IOError, error:

			# [Medium] TODO

			pass

		exit(0)

	def run(self):

		try:

			command = raw_input(">>> ")

			command_list = command.split()

			try:

				command_list[0] = command_list[0].lower()

				if command_list[0] == "clear":

					system("clear")

				elif command_list[0] == "exit":

					self.threads.stop_all_threads()

					self.status = "stopped"

					self.messages.inform(self.messages.CONSOLE_BYE, True, None, False)

					try:

						remove(self.config["lock_file_path"])

					except IOError, error:

						# [Medium] TODO

						pass

				elif command_list[0] == "start":

					try:

						if command_list[1] == "-a":

							Daemon(Priority_Daemon.config["pid_file_path"]).stop()

							Daemon(Wikimetrics_Daemon.config["pid_file_path"]).stop()

							self.threads.start_all_threads()

						elif command_list[1] == "-p":

							Daemon(Priority_Daemon.config["pid_file_path"]).stop()

							self.threads.start_priority_thread()

						elif command_list[1] == "-w":

							Daemon(Wikimetrics_Daemon.config["pid_file_path"]).stop()

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

									urls_added = self.urls.add_url(None, command_list[3])

								else:

									urls_added = self.urls.add_url(command_list[2])

								self.messages.inform(self.messages.URLS_ADDED % {
									"urls_added" : urls_added[0],
									"total_urls" : urls_added[1]
								}, True, None, False)

							except IndexError:

								raise IndexError

						elif command_list[1] == "-rm":

							try:

								if command_list[2] == "-f":

									urls_removed = self.urls.remove_url(None, command_list[3])

								else:

									urls_removed = self.urls.remove_url(command_list[2])

								self.messages.inform(self.messages.URLS_REMOVED % {
									"urls_removed" : urls_removed[0],
									"total_urls" : urls_removed[1]
								}, True, None, False)

							except IndexError:

								raise IndexError

						else:

							raise IndexError

					except IndexError:

						self.messages.inform(self.messages.CONSOLE_URL_OPTIONS, True, None, False)

				elif command_list[0] == "-help":

					self.messages.inform(self.messages.CONSOLE_COMMANDS, True, None, False)

				else:

					self.messages.inform(self.messages.CONSOLE_COMMAND_NOT_FOUND % {
						"command" : command_list[0]
					}, True, None, False)

			except IndexError:

				pass

		except KeyboardInterrupt:

			self.messages.inform(self.messages.CONSOLE_NO_KEYBOARD_INTERRUPT, True, None, False)

		except EOFError:

			self.messages.inform(self.messages.CONSOLE_NO_KEYBOARD_INTERRUPT, True, None, False)
