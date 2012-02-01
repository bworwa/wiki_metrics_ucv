
# Native
from os import system
from os.path import abspath, dirname
from getpass import getuser
from sys import argv

# XCraper
from core.messages import Messages

# User defined
from usr.console import Console
from usr.threads import Threads
from usr.daemon import Daemon

class _Daemon(Daemon):

	def run(self):

		threads = Threads()

		threads.start_priority_thread()

		threads.start_wikimetrics_thread()

if __name__ == "__main__":

	messages = Messages()

	try:

		if argv[1] == "-c":

			system("clear")

			console = Console()

			messages.inform(messages.MAIN_HEADER % {
				"user" : getuser()
			}, True, None, False)

			while console.status == "running":

				console.run()

		elif argv[1] == "-d":

			_daemon = _Daemon(dirname(dirname(abspath(__file__))) + "/tmp/daemon.pid")

			try:

				if argv[2] == "-start":					
			
					_daemon.start()

				elif argv[2] == "-stop":

					_daemon.stop()

				else:

					raise IndexError

			except IndexError:

				messages.inform(messages.MAIN_DAEMON_OPTIONS, True, None, False)

		else:

			raise IndexError

	except IndexError:

		messages.inform(messages.MAIN_OPTIONS, True, None, False)
