
def check_username(username):
	"""
	Function takes as input username input by user and tell if it is valid or not
	"""

	user_valid = True

	# Length Check
	if len(username) <= 1:
		user_valid = False
	elif " " in username:
		user_valid = False

	return user_valid


