import unittest
from plot_map import get_forecast_idx

class test_get_forecast_idx(unittest.TestCase):

	def test_usernames(self):

		self.assertCountEqual(get_forecast_idx(5, 100), [0,21,0,10])
		self.assertCountEqual(get_forecast_idx(90, 100), [79,100,85,100])
		self.assertCountEqual(get_forecast_idx(20, 100), [10,31,15,25])