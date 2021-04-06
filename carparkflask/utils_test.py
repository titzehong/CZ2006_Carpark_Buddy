import unittest
from utils import check_username

class test_check_username(unittest.TestCase):

	def test_usernames(self):

		self.assertAlmostEqual(check_username('Bobby'), True)
		self.assertAlmostEqual(check_username('Bobby '), False)
		self.assertAlmostEqual(check_username(' Bobby'), False)
		self.assertAlmostEqual(check_username(''), False)
		self.assertAlmostEqual(check_username(' '), False)
		self.assertAlmostEqual(check_username('B'), False)
		self.assertAlmostEqual(check_username('1'), False)
		self.assertAlmostEqual(check_username('Bo'), True)