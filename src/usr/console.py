
# Native
from os import getpid, system
from os.path import abspath, dirname
from signal import signal, SIGTERM
import readline

# XCraper
from core.messages import Messages

# User defined
from usr.threads import Threads
from usr.urls import Urls
from usr.daemon import Daemon, Priority_Daemon, Wikimetrics_Daemon
from usr.helpers.control_files import Control_files

class Console:

	config = {
		"lock_file_path" : dirname(dirname(dirname(abspath(__file__)))) + "/tmp/console.lock"
	}

	status = "stopped"

	messages = Messages()

	threads = Threads()

	urls = Urls()

	control_files = Control_files()

	def __init__(self):

		self.status = "running"

		# Create/write .lock file

		self.control_files.create_file(self.config["lock_file_path"], getpid())

		signal(SIGTERM, self.sigterm_handler)

	def __del__(self):

		self.control_files.remove_file(self.config["lock_file_path"])

	def sigterm_handler(self, signal_number, frame):

		self.threads.stop_all_threads()

		exit(0)

	def get_daemon_pid(self, daemon_pid_file_path):

		daemon_pid = self.control_files.get_content(daemon_pid_file_path)

		if daemon_pid:

			return daemon_pid

		return None

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

				elif command_list[0] == "start":

					try:

						if command_list[1] == "-a":

							priority_daemon_pid = self.get_daemon_pid(Priority_Daemon.config["pid_file_path"])

							if priority_daemon_pid:

								self.messages.inform(self.messages.CONSOLE_STOP_DAEMON % {
									"name" : "priority",
									"pid" : int(priority_daemon_pid)
								}, True, None, False)

							else:

								self.threads.start_priority_thread()

							wikimetrics_daemon_pid = self.get_daemon_pid(Wikimetrics_Daemon.config["pid_file_path"])

							if wikimetrics_daemon_pid:

								self.messages.inform(self.messages.CONSOLE_STOP_DAEMON % {
									"name" : "wikimetrics",
									"pid" : int(wikimetrics_daemon_pid)
								}, True, None, False)

							else:

								self.threads.start_wikimetrics_thread()

						elif command_list[1] == "-p":							

							priority_daemon_pid = self.get_daemon_pid(Priority_Daemon.config["pid_file_path"])

							if priority_daemon_pid:

								self.messages.inform(self.messages.CONSOLE_STOP_DAEMON % {
									"name" : "priority",
									"pid" : int(priority_daemon_pid)
								}, True, None, False)

							else:

								self.threads.start_priority_thread()

						elif command_list[1] == "-w":

							wikimetrics_daemon_pid = self.get_daemon_pid(Wikimetrics_Daemon.config["pid_file_path"])

							if wikimetrics_daemon_pid:

								self.messages.inform(self.messages.CONSOLE_STOP_DAEMON % {
									"name" : "wikimetrics",
									"pid" : int(wikimetrics_daemon_pid)
								}, True, None, False)

							else:

								self.threads.start_wikimetrics_thread()

						elif command_list[1] == "-help":

							self.messages.inform(self.messages.CONSOLE_START_OPTIONS, True, None, False)

						else:

							self.messages.inform(self.messages.CONSOLE_INVALID_OPTION % {
								"option" : command_list[1],
								"command" : "start"
							}, True, None, False)

					except IndexError:

						self.messages.inform(self.messages.CONSOLE_NO_OPTION_SPECIFIED % {
							"command" : "start"
						}, True, None, False)

				elif command_list[0] == "stop":

					try:

						if command_list[1] == "-a":

							self.threads.stop_all_threads()

						elif command_list[1] == "-p":

							self.threads.stop_priority_thread()

						elif command_list[1] == "-w":

							self.threads.stop_wikimetrics_thread()

						elif command_list[1] == "-help":

							self.messages.inform(self.messages.CONSOLE_STOP_OPTIONS, True, None, False)

						else:

							self.messages.inform(self.messages.CONSOLE_INVALID_OPTION % {
								"option" : command_list[1],
								"command" : "stop"
							}, True, None, False)

					except IndexError:

						self.messages.inform(self.messages.CONSOLE_NO_OPTION_SPECIFIED % {
							"command" : "stop"
						}, True, None, False)

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

								self.messages.inform(self.messages.CONSOLE_NO_OPTION_SPECIFIED % {
									"command" : "url"
								}, True, None, False)

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

								self.messages.inform(self.messages.CONSOLE_NO_OPTION_SPECIFIED % {
									"command" : "url"
								}, True, None, False)

						elif command_list[1] == "-help":

							self.messages.inform(self.messages.CONSOLE_URL_OPTIONS, True, None, False)

						else:

							self.messages.inform(self.messages.CONSOLE_INVALID_OPTION % {
								"option" : command_list[1],
								"command" : "url"
							}, True, None, False)

					except IndexError:

						self.messages.inform(self.messages.CONSOLE_NO_OPTION_SPECIFIED % {
							"command" : "url"
						}, True, None, False)

				elif command_list[0] == "help":

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
