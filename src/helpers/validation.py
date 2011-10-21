#Native
from re import search, IGNORECASE

class Validation:

	def __init__(self):

		#TODO

		pass

	def __del__(self):

		#TODO

		pass

	def validate_identifier(self, identifier):

		match = search("^[a-z_][a-z0-9_]*", identifier, IGNORECASE)
	
		if match:

			return True

		return False
