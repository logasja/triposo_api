"""Module containing the models used for the API.

The classes here can be used independently of the API.

When instantiating an :class:`Episode`, :class:`Show`, :class:`Season`, or :class:`User`
the ``api`` parameter is optional.
If it is specified, that object will be used to make calls to the
API when needed.

For example, :meth:`Episode.season <Episode.season>` would make a call to the API.
If ``api`` is not specified, ``NotImplementedError`` will be raised if a method that
needs the api is called.

"""

import os
from functools import wraps

import requests


def api_method(func):
    """Decorate methods needing access to the api.

    This decorator ensures that methods that need to make a call to the
    api are only run if access to the api is available.
    If access to it is not available, ``NotImplementedError`` will be raised.

    """
    @wraps(func)
    def api_call(*args, **kwargs):
        if args[0]._api:
            return func(*args, **kwargs)
        else:
            raise NotImplementedError
    return api_call


class ApiObject(object):
    """Base class for resources available from the API.

    Resources such as Episodes, Seasons, Shows, and Users should inherit from this class.

    """

    def __init__(self):  # noqa: D102
        self._thumbnail = {}

    def _build(self, model_json):
        """Assemble an object from a JSON representation.

        Uses ``self.attrs`` to pull values from ``model_json`` and create object attributes.

        Args:
            model_json: JSON representation of an API resource.

        Raises:
            KeyError: if the key from ``self.attrs`` is not a key in ``model_json``

        """
        for key, value in self.attrs.items():
            try:
                # TODO use setattr(self, key, value) instead?
                self.__dict__.update({key: ApiObject._get_from_dict(model_json, value)})
            except KeyError:
                self.__dict__.update({key: None})

    @staticmethod
    def _get_from_dict(data_dict, map_list):
        """Retrieve the value corresponding to ``map_list`` in ``data_dict``.

        If ``map_list`` is a string, it is used directly as a key of ``data_dict``.
        If ``map_list`` is a list or tuple, each item in it is used recusively as a key.

        Args:
            data_dict (dict): The dictionary to retrieve value from.
            map_list (list, tuple or str): The key(s) to use in data_dict.

        Returns:
            The value corresponding to the given key(s).

        """
        if isinstance(map_list, (list, tuple)):
            for k in map_list:
                data_dict = data_dict[k]
        else:
            data_dict = data_dict[map_list]
        return data_dict

    def __eq__(self, other):
        """Define equality of two API objects as having the same type and attributes."""
        return (type(self) == type(other) and
                dict((k, self.__dict__[k]) for k in self.attrs.keys()) ==
                dict((k, other.__dict__[k]) for k in other.attrs.keys()))

    def __repr__(self):
        """Nicer printing of API objects."""
        return str(dict((k, self.__dict__[k]) for k in self.attrs.keys()))

class Location(ApiObject):
    """Class representing a Location.

    Attributes:
        id_ (str):              Location identifier.
        country_id (str):       The location ID of the country this location is contained within.
        country_code (str):     Agreed upon identifier for countries.
        intro (str):            Medium-length string describing location.
        name (str):             The human-readable name of the location.
        parent_id (str):        The ID of the parent location.
        score (float):          An indicator of the importance of the location, between 0 and 10.
        snippet (str):          A short string describing the location.
        tag_labels (list):      The labels of the tags that apply to this location.
        type (str):             (city, city_state, island, national_park, region, country).
    """

    def __init__(self, location_json, api=None):
        """Take in a JSON representation of a article and convert it into a Article Object.

        Args:
            article_json (json):       JSON representation of a article resource.
        """
        super(Location, self).__init__()
        self.attrs = {
            "id_":          "id",
            "country_id":   "country_id",
            "country_code": "country_code",
            "intro":        "intro",
            "name":         "name",
            "parent_id":    "parent_id",
            "score":        "score",
            "snippet":      "snippet",
            "tag_labels":   "tag_labels",
            "type":         "type"
        }
        self._build(location_json)
        self._api = api

class DayPlan(ApiObject):
    """Class representing a Day Plan.

    Attributes:
        seed (int):             The seed used to generate this dayplan.
        location (Location):    Location in which the plan takes place.
        hotel (POI):            Hotel description where day plan is based from, if supplied
        days (list):            Day by day description of the day plan.
    """
    def __init__(self, dayplan_json, api=None):
        """Take in a JSON representation of a dayplan and convert it to a DayPlan Object.

        Args:
            dayplan_json (json):        JSON representation of a article resource.
        """
        super(DayPlan, self).__init__()
        self.attrs = {
            "seed":         "seed",
            "_location":    "location",
            "_hotel":       "hotel",
            "_days":        "days"
        }
        self._build(dayplan_json)
        self._api = api
        self.day = []
        self.location = None
        self.hotel = None
        try:
            self.location = Location(self._location)
        except:
            print("Unable to build Location object")
        try:
            self.hotel = PointOfInterest(self._hotel)
        except:
            print("Unable to build hotel POI")
        try:
            for day in self._days:
                self.day.append(Itinerary(day))
        except:
            print("Unable to build itinerary list")

class PointOfInterest(ApiObject):
    """Class representing a Point of Interest.

    Attributes:
        id_ (str):              The machine-readable identifier of POI.
        name (str):             The human-readable name of this POI.
        price (int):            Price indication for this POI, if available. 1=cheap, 2=medium, 3=expensive.
        intro (str):            A medium-length version of the content.
        location_id (str):      The ID of the location this POI is contained within.
        score (float):          An indicator of the importance of this POI, generally between 0 and 10.
        snippet (str):          A short version of the content.
        tag_labels (list):      The labels of the tags that apply to this POI
    """

    def __init__(self, poi_json, api=None):
        """Take in a JSON representation of a poi and convert it to a PointOfInterest Object.

        Args:
            poi_json (json):            JSON representation of a poi resource.
        """
        super(PointOfInterest, self).__init__()
        self.attrs = {
            "id_":          "id",
            "name":         "name",
            "price":        "price_tier",
            "intro":        "intro",
            "location_id":  "location_id",
            "score":        "score",
            "snippet":      "snippet",
            "tag_labels":   "tag_labels"
        }
        self._build(poi_json)
        self._api = api

class Itinerary(ApiObject):
    """Class representing a Itinerary.

    Attributes:
        date (str):             A title for this itinerary.
        items (list):           A longer description of this itinerary item.
    """

    def __init__(self, itinerary_json, api=None):
        """Take in a JSON representation of a itinerary and convert it to a Itinerary Object.

        Args:
            itinerary_json (json): JSON representation of an itinerary
        """
        super(Itinerary, self).__init__()
        self.attrs = {
            "date":         "date",
            "_items":        "itinerary_items"
        }
        self._build(itinerary_json)
        self._api = api
        self.items = []
        try:
            for item in self._items:
                self.items.append(ItineraryItem(item))
        except Exception:
            print("Oops can't make ItineraryItems.")

class ItineraryItem(ApiObject):
    """Class representing a Itinerary Item.

    Attributes:
        title (str):            A title for this itinerary item.
        description (str):      A longer description of this itinerary item.
        poi (POI):              The POI object corresponding to this itinerary item.
    """

    def __init__(self, itinerary_item_json, api=None):
        """Take in a JSON representation of a itinerary item and convert it to a ItineraryItem Object.

        Args:
            itinerary_item_json (json): JSON representation of a itinerary item
        """
        super(ItineraryItem, self).__init__()
        self.attrs = {
            "description":  "description",
            "title":        "title",
            "_poi":          "poi"
        }
        self._build(itinerary_item_json)
        self._api = api
        try:
            self.poi = PointOfInterest(self._poi)
        except Exception:
            print("oops can't make a POI.")

class Tag(ApiObject):
    """Class representing a Tag Item.

    Attributes:
        tour_count (int):       The number of tours that have this tag.
        article_count (int):    The number of articles with this tag.
        label (str):            A machine-readable label for this tag - only unique within a location_id.
        location_id (str):      The ID of the location this tag applies to.
        name (str):             A human-readable name for this tag.
        poi_count (int):        Number of POIs with this tag.
        score (int):            The score of this tag, between 0 and ~10.
        short_name (str):       A short human-readable name for this tag.
        snippet (str):          A short string describing the tag.
        tour_count (int):       The number of tours that have this tag.
        type (tag_type):        The general type of tag.
    """

    def __init__(self, tag_json, api=None):
        """Take in a JSON representation of a tag item and convert it to a Tag Object.

        Args:
            tag_json (json): JSON representation of a tag item
        """
        print(tag_json)
        super(Tag, self).__init__()
        self.attrs = {
            "tour_count":       "tour_count",
            "article_count":    "article_count",
            "label":            "label",
            "location_id":      "location_id",
            "name":             "name",
            "poi_count":        "poi_count",
            "score":            "score",
            "short_name":       "short_name",
            "snippet":          "snippet",
            "type":             "type"
        }
        self._build(tag_json)
        self._api = api