
# Native
from os import system
from getpass import getuser
from sys import argv
from time import sleep

# XCraper
from core.messages import Messages

# User defined
from usr.console import Console
from usr.daemon import Daemon, Priority_Daemon, Wikimetrics_Daemon

if __name__ == "__main__":

	messages = Messages()

	try:

		if argv[1] == "-c":

			system("clear")

			messages.inform(messages.MAIN_HEADER % {
				"user" : getuser()
			}, True, None, False)

			console = Console()

			while console.status == "running":

				console.run()

		elif argv[1] == "-d":

			try:

				if argv[2] == "start":

					if argv[3] == "-p":

						Priority_Daemon(Priority_Daemon.config["pid_file_path"]).start()

					elif argv[3] == "-w":

						Wikimetrics_Daemon(Wikimetrics_Daemon.config["pid_file_path"]).start()

					else:

						raise IndexError

					while True:

						sleep(3600)

				elif argv[2] == "stop":

					if argv[3] == "-p":

						Daemon(Priority_Daemon.config["pid_file_path"]).stop()

					elif argv[3] == "-w":

						Daemon(Wikimetrics_Daemon.config["pid_file_path"]).stop()

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
