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

class Article(ApiObject):
    """Class representing a Article.

    Attributes:
        id_ (str):              Article identifier.
        intro (str):            Article Intro.
        location_ids (list):    Summary of the show.
        name (str):             Human readable title for article.
        score (float):          Indicator of the importance of article, between 0 and 10
        snippet (str):          Short version of the content of article.
        # content (Content):      The content of this article.
        # tag_labels (list):      Labels of the tags that apply to this article.
        tags (list):            Full tags that apply to this article.
    """

    def __init__(self, article_json, api=None):
        """Take in a JSON representation of a article and convert it into a Article Object.

        Args:
            article_json (json):       JSON representation of a article resource.
            api (object, optional):    Object that implements the API
                                       (see :class:`~triposo_api.api.triposo_api`).
                                       This will be used to make calls to the API when needed.
        """
        super(Article, self).__init__()
        self._api = api
        self.attrs = {
            "id_":          "id",
            "name":         "name",
            "intro":        "intro",
            "score":        "score",
            "snippet":      "snippet",
            # "tag_labels":   "tag_labels",
            "tags":         "tags"
        }
        self._build(article_json)
        # try:
        #     content_json = article_json['content']
        #     self._content = Content(content_json)
        # except KeyError:
        #     # Doesn't have thumbnail
        #     pass

    @property
    @api_method
    def seasons(self):
        """Return all seasons of the Show."""
        if not self._seasons:
            self._seasons = self._api.show_seasons(self.id_)
        return self._seasons

    @property
    def episodes(self):
        """Return all the episodes of the Show."""
        if not self._episodes:
            self._episodes = []
            for season in self.seasons:
                self._episodes.extend(season.episodes)
        return self._episodes

    def get_thumbnail(self, quality):
        """Return the URL of the show's thumbnail at specified quality.

        Args:
            quality (str):  possible values are (in order from smallest to largest): "tb", "sm", "md", "lg".

        Returns:
            str: URL of the thumbnail or ``None`` if thumbnail not available at specified quality.

        """
        try:
            return self._thumbnail[quality]
        except KeyError:
            return None

    @property
    def cover_picture(self):
        """Return the default sized cover picture URL.

        If not available, return the next most 'appropriate' sized thumbnail.
        'Most appropriate' is defined as largest, as the cover picture is usually
        used as a large backdrop.

        Returns:
            str: URL of the cover picture or ``None`` if no cover picture is available.

        Examples:
            >>> some_show.cover_picture
            'http://s3.amazonaws.com/cdn.roosterteeth.com/uploads/images/14a811b0-b0f1-4b08-a65b-1c565d6d153f/original/21-1458935312881-ots_hero.png'

        """
        for picture in ["lg", "tb", "sm", "md"]:
            try:
                return self._cover_picture[picture]
            except KeyError:
                continue
        return None
