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

    @property
    def thumbnail(self):
        """Return the default sized thumbnail URL.

        Default is defined as the smallest.

        """
        for thumb in ["tb", "sm", "md", "lg"]:
            try:
                return self._thumbnail[thumb]
            except KeyError:
                continue
        return None

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
