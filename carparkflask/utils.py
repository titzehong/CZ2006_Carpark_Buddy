
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


def check_password(password):
	"""
	Password must be at least 8 characters long, no whitespaces
	"""

	password_valid = True

	# Length Check
	if len(password) < 8:
		password_valid = False
	elif " " in password:
		password_valid = False

	return password_valid

