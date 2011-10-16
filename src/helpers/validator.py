from re import search, IGNORECASE

def validate_identifier(identifier):

	match = search("^[a-z_][a-z0-9_]*", identifier, IGNORECASE)

	if match:

		return True

	return False 
