from unittest import TestCase

from data import charge_stations


class TestDrivers(TestCase):
    def test_reduce(self):
        out = charge_stations.get_multipoints([[1,2],[3,4]])
        self.assertEqual("LINESTRING( 2 1, 4 3)", out)