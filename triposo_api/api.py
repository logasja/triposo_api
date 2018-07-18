"""Module containing the interface to the Api.

Currently access:
Location
PointOfInterest
DayPlan
Itinerary

"""

import posixpath
from functools import wraps

from cache_requests import Session
import requests
from triposo_api import models, config

class Api(object):
    """Main class of the API.

    Create an instance of this to access the api.

    """

    def __init__(self, account_id = config.API_ACCOUNT, token = config.API_KEY):
        """Create an api object.

        Args:
            api_key (str, optional): api key to use.
                If one is not supplied, a default one will be generated and used.

        """
        self.__session = Session()
        self.__session.headers['X-Triposo-Account'] = account_id
        self.__session.headers['X-Triposo-Token'] = token

    def __get_data(self, url, params=None):
        """Get the data at the given URL, using supplied parameters.

        Args:
            url (str):               The URL to retrieve data from.
            params (dict, optional): Key-value pairs to include when making the request.

        Returns:
            json: The JSON response.

        """
        response = self.__session.get(url, params=params)
        # Check status code
        if response.status_code == 401:
            # TODO Bad api key
            response.raise_for_status()
        elif response.status_code == 404:
            # Api Item does not exist
            return None
        elif response.status_code != requests.codes.ok:
            response.raise_for_status()
        try:
            json_data = response.json()
            # print(json_data)
            if json_data['estimated_total'] == 1:
                # print("A single one")
                return json_data['results'][0]
            else:
                # print("Multiple responses")
                return json_data['results']
        except ValueError:
            # Parsing json response failed
            pass

    def _arguments_from_kwargs(self, arguments):
        url = ''
        for key in arguments:
            url += key + '=' + str(arguments[key]) + '&'
        url = url.rstrip('&')
        return url

    def __build_response(self, path, model_class):
        """Retrieve data from given path and load it into an object of given model class.

        Args:
            path (str):         Path of API to send request to.
            model_class (type): The type of pbject to build using the response from the API.

        Returns:
            object: Instance of the specified model class.

        """
        data = self.__get_data(posixpath.join(config.END_POINT, path))
        if not data:
            # TODO raise exception complaining that no data was retrieved from api?
            return None
        return model_class(data, self)

    def __get_multiple(self, path, model_class):
        """Retrieve from API endpoint that returns a list of items.

        Args:
            model (type): The type of object to build using the response from the API.
            path (str):   The path of API to send request to.

        Returns:
            list: A list containing items of type model_class.

        """
        url = posixpath.join(config.END_POINT, path)
        data = self.__get_data(url)
        if not data:
            return None
        items = []
        # print(data)
        for json_item in data:
            item = model_class(json_item, self)
            items.append(item)
        return items

    def location(self, **kwargs):
        """Retrieve the episode corresponding to the specified id.

        Args:
            location_id (int): ID of the location to retrieve.

        Returns:
            Location: Location instance.

        """
        url = self._arguments_from_kwargs(kwargs)
        return self.__build_response('location.json?' + url, models.Location)

    def locations(self, **kwargs):
        """Get a list of locations.

        Args:
            kwargs:     Collection of arguments for locations

        Returns:
            iterable: An iterable collection of :class:`Locations <triposo_api.models.Location>`.

        """
        url = self._arguments_from_kwargs(kwargs)
        return self.__get_multiple('location.json?' + url, models.Location)

    def day_planner(self, **kwargs):
        """Get day plans

        Args:
            kwargs:     Collection of arguments for locations

        Returns:
            iterable: An iterabile collection of :class:`
        """
        url = self._arguments_from_kwargs(kwargs)
        return self.__build_response('day_planner.json?' + url, models.DayPlan)

    def point_of_interest(self, **kwargs):
        """Get single point of interest

        Args:
            kwargs:     Collection of arguments for poi

        Returns:
            POI:    A PointOfInterest class object
        """
        url = self._arguments_from_kwargs(kwargs)
        return self.__build_response('poi.json?' + url, models.PointOfInterest)

    def points_of_interest(self, **kwargs):
        """Get list of points of interest.

        Args:
            kwargs:     Collection of arguments for poi

        Returns:
            list(POI):  A list of PointOfInterest objects
        """
        url = self._arguments_from_kwargs(kwargs)
        return self.__get_multiple('poi.json?' + url, models.PointOfInterest)

    def tags(self, **kwargs):
        """Get list of tags.

        Args:
            kwargs:     Collection of arguments for tags.

        Returns:
            list(Tag):  A list of Tag objects
        """
        url = self._arguments_from_kwargs(kwargs)
        return self.__get_multiple('tag.json?' + url, models.Tag)

    def get_common_tag_labels(self):
        """Get list of the most common tags.

        Returns:
            list(Object):   A list of objects
        """
        return self.__get_data(posixpath.join(config.END_POINT, 'common_tag_labels.json'))