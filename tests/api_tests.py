import unittest
import context
import json
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

    def test_day_planner(self):
        lisbon = self._api.day_planner(location_id='Lisbon', hotel_poi_id='T__4b30a4f2881c', start_date='2017-06-03',
                                       arrival_time='14:33', end_date='2017-06-06', departure_time='16:55')
        self.assertIsNotNone(lisbon)
        self.assertIsNotNone(lisbon.location)
        self.assertIsNotNone(lisbon.hotel)
        self.assertFalse(len(lisbon.day) == 0)

    def test_point_of_interest(self):
        poi = self._api.point_of_interest(id='W__5013364', fields='all')
        self.assertIsNotNone(poi)
        self.assertEqual(poi.location_id, "Paris")
        self.assertIn('sightseeing', poi.tag_labels)

    def test_points_of_interest_tokyo(self):
        pois = self._api.points_of_interest(location_id='Tokyo', annotate='trigram:gold', trigram='>=0.3',
                                            count=10, fields='id,name,score,snippet,location_id,tag_labels',
                                            order_by='-score')

        self.assertIsNotNone(pois)
        self.assertEqual(2, len(pois))
        self.assertEqual(pois[0].name, 'Golf 5')
        self.assertEqual(pois[1].name, 'GOLD FOUNTAIN')

    def test_points_of_interest_paris(self):
        pois = self._api.points_of_interest(annotate='trigram:Eiffel',trigram='>=0.3',location_id='Paris',
                                            count=10, fields='id,name,score,snippet,location_id,tag_labels',
                                            order_by='-score')

        self.assertIsNotNone(pois)
        self.assertEqual(10, len(pois))

    def test_tag_sydney(self):
        tags = self._api.tags(location_id='Sydney', 
                              count=10, 
                              order_by='-score')
        self.assertIsNotNone(tags)
        self.assertEqual(10, len(tags))

    def test_architecture_tags(self):
        architecture = self._api.tags(location_id='Berlin',
                                      type='architecture')
        self.assertIsNotNone(architecture)
        self.assertEqual(10, len(architecture))

    def test_practical_tags(self):
        practicals = self._api.tags(location_id='Saint_Petersburg',
                                    type='practical')

        self.assertIsNotNone(practicals)
        self.assertEqual(10, len(practicals))

    def test_get_common_tag_labels(self):
        tag_labels = self._api.get_common_tag_labels()
        with open('tags.txt', 'w') as outfile:
            json.dump(tag_labels, outfile)

if __name__ == '__main__':
    api_test = unittest.TestLoader().loadTestsFromTestCase(TestAPIGeneral)
    unittest.TextTestRunner(verbosity=1).run(api_test)