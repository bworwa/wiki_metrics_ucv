#External [dependency]
from pycurl import Curl

class Request:

	current_headers = {}

	def __init__(self):

		#TODO

		pass

	def __del__(self):

		#TODO

		pass

	def head_request_callback(self, response):
		
		response = response.strip()

		if response:

			if ":" in response:

				header = response.split(":")

				self.current_headers[header[0].rstrip()] = header[1].lstrip()

			else:

				self.current_headers["Response-Code"] = response.lstrip()

	def head(self, url, user_agent):

		self.current_headers = {}

		request = Curl()

		request.setopt(request.URL, url)

		request.setopt(request.USERAGENT, str(user_agent))

		request.setopt(request.NOBODY, True)

		#These two should be configurable and should be setted in scraper.py
		request.setopt(request.FOLLOWLOCATION, True)

		request.setopt(request.MAXREDIRS, 3)

		request.setopt(request.HEADERFUNCTION, self.head_request_callback)

		request.perform()

		request.close()
