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

	def __init__(self, pid_file, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):

		self.stdin = stdin

		self.stdout = stdout

		self.stderr = stderr

		self.pid_file = pid_file

		self.messages.DAEMONS = "daemons"
	
	def daemonize(self):

		"""
		Do the UNIX double-fork magic, see Stevens' "Advanced 
		Programming in the UNIX Environment" for details (ISBN 0201563177)
		Http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
		"""

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

		# Redirect standard file descriptors

		stdout.flush()

		stderr.flush()

		stdin_file = file(self.stdin, 'r')

		stdout_file = file(self.stdout, 'a+')

		stderr_file = file(self.stderr, 'a+', 0)

		dup2(stdin_file.fileno(), stdin.fileno())

		dup2(stdout_file.fileno(), stdout.fileno())

		dup2(stderr_file.fileno(), stderr.fileno())

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

		if pid:

			self.messages.raise_error(self.messages.DAEMON_ALREADY_RUNNING % {
				"pid_file" : self.pid_file
			}, self.messages.DAEMONS)

		# Start the daemon

		self.daemonize()

		self.run()

	def stop(self):

		"""
		Stop the daemon
		"""

		# Get the pid from the .pid file

		try:

			pid_file = file(self.pid_file, 'r')

			pid = int(pid_file.read().strip())

			pid_file.close()

		except IOError:

			pid = None

		if not pid:

			self.messages.raise_error(self.messages.DAEMON_NOT_RUNNING % {
				"pid_file" : self.pid_file
			}, self.messages.DAEMONS)

		# Try killing the daemon process

		try:

			while True:

				kill(pid, SIGTERM)

				sleep(0.5)

			remove(self.pid_file)

		except OSError, error:

			if error.errno == ESRCH:

				if exists(self.pid_file):

					remove(self.pid_file)

			else:

				self.messages.raise_error(error.strerror, self.messages.DAEMONS)

class Priority_Daemon(Daemon):

	def run(self):

		Threads().start_priority_thread()

class Wikimetrics_Daemon(Daemon):

	def run(self):

		Threads().start_wikimetrics_thread()
