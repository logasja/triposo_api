import unittest
import context
from triposo_api.api import Api
from unittest import mock

class TestAPIGeneral(unittest.TestCase):
    def setUp(self):
        self._api = Api(None, None)

    def test_arguments_from_kwargs(self):
        def tst(**kwargs):
            url = self._api._arguments_from_kwargs(kwargs)
            return url
        url = tst(hello='world', why='not', test='arg')
        self.assertEqual(url, 'hello=world&why=not&test=arg')

    def test_location(self):
        amsterdam = self._api.location(id='Amsterdam', fields='all')
        self.assertIsNotNone(amsterdam)
        self.assertIsNotNone(amsterdam.name)
        self.assertIsNotNone(amsterdam.type)

    def test_find_country(self):
        koreas = self._api.locations(tag_labels='country', annotate='trigram:Korea', trigram='>=0.3',
                                     count=10, fields='id,name,score,snippet', order_by='-score')
        self.assertIsNotNone(koreas)
        self.assertIsNotNone(koreas[0].name)
        self.assertIsNotNone(koreas[1].name)

if __name__ == '__main__':
    api_test = unittest.TestLoader().loadTestsFromTestCase(TestAPIGeneral)
    unittest.TextTestRunner(verbosity=1).run(api_test)