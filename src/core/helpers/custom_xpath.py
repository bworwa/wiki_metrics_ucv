
"""Core libraries, do not change"""

# External
from xpath import find, findvalue

class Xpath:

	def __init__(self):

		# [Low] TODO

		pass

	def __del__(self):

		# [Low] TODO

		pass

	def find(self, query, context, get_value, charset, result_list):

		"""
		Appends to 'result_list' the result of applying the XPath query 'query' to the minidom Document 'context'
		'get_value' (True/False) will determine whether to use 'xpath.find' or 'xpath.findValue'

		All the results are encoded using the specified 'charset'
		"""

		if get_value:

			xpath_result = findvalue(query, context)

			if xpath_result:

				result_list.append(xpath_result.encode(charset))

			else:

				result_list.append(None)

		else:

			xpath_result = find(query, context)

			if xpath_result:

				for result in xpath_result:

					if result.nodeType == 2:

						result_list.append(result.value.encode(charset))

					elif result.nodeType == 3 or result.nodeType == 4 or result.nodeType == 6 or result.nodeType == 7:

						result_list.append(result.data.encode(charset))

					else:

						result_list.append(result.toxml().encode(charset))

			else:

				result_list.append(None)
