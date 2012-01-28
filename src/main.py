
# Native
from os import system
from getpass import getuser
from sys import stdout

# User defined
from usr.console import Console

if __name__ == "__main__":

	HEADER = """Wiki Metrics UCV (https://github.com/bworwa/wiki_metrics_ucv)
Welcome """ + getuser() + """!

"""

	system("clear")

	console = Console()

	stdout.write(HEADER)

	while console.status == "running":

		console.run()
