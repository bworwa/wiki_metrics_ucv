#!/usr/bin/env python

# Daemon class author: Sander Marechal
# Rewritten by: Benjamin Worwa

# Native
from os import fork, chdir, setsid, umask, dup2, getpid, kill
from os.path import abspath, dirname
from sys import modules, stderr, stdin, stdout, exit
from errno import ESRCH
from signal import signal, SIGTERM
from time import sleep

# User defined
from core.messages import Messages
from usr.threads import Threads
from usr.helpers.control_files import Control_Files
import usr.console

class Daemon:

	"""
	A generic daemon class.
	
	Usage: subclass the Daemon class and override the run() method
	"""

	messages = Messages()

	threads = Threads()

	control_files = Control_Files()

	def __init__(self, pid_file_path, usr_stdin = "/dev/null", usr_stdout = "/dev/null", usr_stderr = "/dev/null"):

		self.pid_file_path = pid_file_path

		self.stderr = usr_stderr

		self.stdin = usr_stdin

		self.stdout = usr_stdout

		self.messages.DAEMONS = "daemons"

	def __del__(self):

		self.control_files.remove_file(self.pid_file_path)
	
	def daemonize(self):

		"""
		Do the UNIX double-fork magic, see Stevens' "Advanced 
		Programming in the UNIX Environment" for details (ISBN 0201563177)
		Http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
		"""

		self.messages.inform(self.messages.STARTING_DAEMON % {
			"separator" : "... "
		}, False, self.messages.DAEMONS)

		if(self.control_files.file_exists(usr.console.Console.config["lock_file_path"])):

			self.messages.raise_error(self.messages.DAEMON_CONSOLE_ALREADY_RUNNING, self.messages.DAEMONS)

		parent_pid = getpid()

		try:

			pid = fork()

			if pid > parent_pid:

				# Exit from the first parent

				exit(0)

		except OSError, error:

			self.messages.raise_error(self.messages.DAEMON_FORK_FAILED % {
				"number" : "1",
				"errno" : error.errno,
				"error" : error.strerror
			}, self.messages.DAEMONS)

		# Decouple from parent environment

		chdir("/")

		setsid()

		umask(0)

		# Do second fork

		try:

			pid = fork()

			if pid > parent_pid:

				# Exit from the second parent

				exit(0)

		except OSError, error:

			self.messages.raise_error(self.messages.DAEMON_FORK_FAILED % {
				"number" : "2",
				"errno" : error.errno,
				"error" : error.strerror
			}, self.messages.DAEMONS)

		# Create/write .pid file

		self.control_files.create_file(self.pid_file_path, getpid())

		self.messages.inform(self.messages.DAEMON_OK, True, self.messages.DAEMONS)

		# Redirect the standard file descriptors

		stderr.flush()

		stdout.flush()

		stderr_file = open(self.stderr, 'a+', 0)

		stdin_file = open(self.stdin, 'r')

		stdout_file = open(self.stdout, 'a+')

		dup2(stderr_file.fileno(), stderr.fileno())

		dup2(stdin_file.fileno(), stdin.fileno())

		dup2(stdout_file.fileno(), stdout.fileno())

	def start(self):

		"""
		Start the daemon
		"""

		self.stop(False)

		self.daemonize()

		self.run()

	def stop(self, console_output = True):

		"""
		Stop the daemon
		"""

		if console_output:

			self.messages.inform(self.messages.STOPPING_DAEMON % {
				"separator" : "... "
			}, False, self.messages.DAEMONS)

		# Get the pid from the .pid file

		try:

			pid = int(self.control_files.get_content(self.pid_file_path))

		except TypeError:

			pid = None

			self.control_files.remove_file(self.pid_file_path)

		# Try killing the daemon process

		if pid:

			try:

				while True:

					kill(pid, SIGTERM)

					sleep(0.5)

			except OSError, error:

				if not error.errno == ESRCH:

					self.messages.raise_error(error.strerror, self.messages.DAEMONS)

		if console_output:

			self.messages.inform(self.messages.DAEMON_OK, True, self.messages.DAEMONS)

class Priority_Daemon(Daemon):

	config = {
		"pid_file_path" : dirname(dirname(dirname(abspath(__file__)))) + "/tmp/priority_daemon.pid"
	}

	def run(self):

		signal(SIGTERM, self.sigterm_handler)

		self.threads.start_priority_thread()

	def sigterm_handler(self, signal_number, frame):

		self.threads.stop_priority_thread()

		exit(0)

class Wikimetrics_Daemon(Daemon):

	config = {
		"pid_file_path" : dirname(dirname(dirname(abspath(__file__)))) + "/tmp/wikimetrics_daemon.pid"
	}

	def run(self):

		signal(SIGTERM, self.sigterm_handler)

		self.threads.start_wikimetrics_thread()

	def sigterm_handler(self, signal_number, frame):

		self.threads.stop_wikimetrics_thread()

		exit(0)
