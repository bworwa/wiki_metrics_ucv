#!/usr/bin/env python

# Daemon class author: Sander Marechal
# Rewritten by: Benjamin Worwa

# Native
from os import fork, chdir, setsid, umask, dup2, getpid, kill, remove
from os.path import exists
from sys import stderr, stdin, stdout, exit
from errno import ESRCH
from signal import SIGTERM
from time import sleep

# User defined
from core.messages import Messages
from usr.threads import Threads

class Daemon:

	"""
	A generic daemon class.
	
	Usage: subclass the Daemon class and override the run() method
	"""

	messages = Messages()

	threads = Threads()

	def __init__(self, pid_file, usr_stdin = "/dev/null", usr_stdout = "/dev/null", usr_stderr = "/dev/null"):

		self.pid_file = pid_file

		self.stderr = usr_stderr

		self.stdin = usr_stdin

		self.stdout = usr_stdout

		self.messages.DAEMONS = "daemons"
	
	def daemonize(self):

		"""
		Do the UNIX double-fork magic, see Stevens' "Advanced 
		Programming in the UNIX Environment" for details (ISBN 0201563177)
		Http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
		"""

		self.messages.inform(self.messages.STARTING_DAEMON % {
			"separator" : "... "
		}, False, self.messages.DAEMONS)

		try:

			pid = fork()

			if pid > 0:

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

			if pid > 0:

				# Exit from the second parent

				exit(0)

		except OSError, error:

			self.messages.raise_error(self.messages.DAEMON_FORK_FAILED % {
				"number" : "2",
				"errno" : error.errno,
				"error" : error.strerror
			}, self.messages.DAEMONS)

		self.messages.inform(self.messages.DAEMON_OK, True, self.messages.DAEMONS)

		# Redirect the standard file descriptors

		stderr.flush()

		stdout.flush()

		stderr_file = file(self.stderr, 'a+', 0)

		stdin_file = file(self.stdin, 'r')

		stdout_file = file(self.stdout, 'a+')

		dup2(stderr_file.fileno(), stderr.fileno())

		dup2(stdin_file.fileno(), stdin.fileno())

		dup2(stdout_file.fileno(), stdout.fileno())

		# Create/write .pid file

		file(self.pid_file, 'w').write(str(getpid()))

	def start(self):

		"""
		Start the daemon
		"""

		# Check for a .pid file to see if there's a daemon already running

		try:

			pid_file = file(self.pid_file, 'r')

			pid = int(pid_file.read().strip())

			pid_file.close()

		except IOError:

			pid = None

		except TypeError:

			pid = None

		if pid:

			self.messages.inform(self.messages.DAEMON_ALREADY_RUNNING % {
				"pid" : pid
			}, True, self.messages.DAEMONS)

		else:

			# Start the daemon

			self.daemonize()

			self.run()

	def stop(self):

		"""
		Stop the daemon
		"""

		self.messages.inform(self.messages.STOPPING_DAEMON % {
			"separator" : "... "
		}, False, self.messages.DAEMONS)

		# Get the pid from the .pid file

		try:

			pid_file = file(self.pid_file, 'r')

			pid = int(pid_file.read().strip())

			pid_file.close()

		except IOError:

			pid = None

		# Try killing the daemon process

		try:

			while True:

				kill(pid, SIGTERM)

				sleep(0.5)

		except OSError, error:

			if error.errno == ESRCH:

				if exists(self.pid_file):

					remove(self.pid_file)

					self.messages.inform(self.messages.DAEMON_OK, True, self.messages.DAEMONS)

			else:

				self.messages.raise_error(error.strerror, self.messages.DAEMONS)

		except TypeError:

			# There was no .pid file or pid was not an integer. We asume that the daemon is not running

			self.messages.inform(self.messages.DAEMON_OK, True, self.messages.DAEMONS)

class Priority_Daemon(Daemon):

	def run(self):

		self.threads.start_priority_thread()

class Wikimetrics_Daemon(Daemon):

	def run(self):

		self.threads.start_wikimetrics_thread()
