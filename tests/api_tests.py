import unittest
from triposo_api.api import Api

class TestAPIGeneral(unittest.TestCase):
    def setUp(self):
        self._api = Api()

    def test_location(self):
        bangkok = self._api.location('Bangkok')
        print(bangkok)