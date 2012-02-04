
# Native
from os import system
from os.path import abspath, dirname
from getpass import getuser
from sys import argv, exit

# XCraper
from core.messages import Messages

# User defined
from usr.console import Console
from usr.daemon import Daemon, Priority_Daemon, Wikimetrics_Daemon

if __name__ == "__main__":

	priority_daemon_pid_file_path = dirname(dirname(abspath(__file__))) + "/tmp/priority_daemon.pid"

	wikimetrics_daemon_pid_file_path = dirname(dirname(abspath(__file__))) + "/tmp/wikimetrics_daemon.pid"

	messages = Messages()

	try:

		if argv[1] == "-c":

			system("clear")

			console = Console(priority_daemon_pid_file_path, wikimetrics_daemon_pid_file_path)

			messages.inform(messages.MAIN_HEADER % {
				"user" : getuser()
			}, True, None, False)

			while console.status == "running":

				console.run()

		elif argv[1] == "-d":

			# Disabled daemon mode until further notice to avoid data corruption

			exit(0)

			try:

				if argv[2] == "-start":

					if argv[3] == "-a":
			
						Priority_Daemon(priority_daemon_pid_file_path).start()

						Wikimetrics_Daemon(wikimetrics_daemon_pid_file_path).start()

					elif argv[3] == "-p":

						Priority_Daemon(priority_daemon_pid_file_path).start()

					elif argv[3] == "-w":

						Wikimetrics_Daemon(wikimetrics_daemon_pid_file_path).start()

					else:

						raise IndexError

				elif argv[2] == "-stop":

					if argv[3] == "-a":
			
						Daemon(priority_daemon_pid_file_path).stop()

						Daemon(wikimetrics_daemon_pid_file_path).stop()

					elif argv[3] == "-p":

						Daemon(priority_daemon_pid_file_path).stop()

					elif argv[3] == "-w":

						Daemon(wikimetrics_daemon_pid_file_path).stop()

					else:

						raise IndexError

				else:

					raise IndexError

			except IndexError:

				raise IndexError

		else:

			raise IndexError

	except IndexError:

		messages.inform(messages.MAIN_OPTIONS, True, None, False)
