"""Module containing the interface to the Api.

Currently access to  is provided.

Todo:

"""

import posixpath
from functools import wraps

import requests
from triposo_api import models, config

class Api(object):
    """Main class of the API.

    Create an instance of this to access the api.

    """

    def __init__(self, account_id = config.ACCOUNT_ID, token = config.TOKEN_SECRET):
        """Create an api object.

        Args:
            api_key (str, optional): api key to use.
                If one is not supplied, a default one will be generated and used.

        """
        self.__session = requests.Session()
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
        # print(url)
        # print(response.status_code)
        # print(response.json()['results'])
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
            return response.json()['results'][0]
        except ValueError:
            # Parsing json response failed
            pass

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

    def __get_multiple(self, model_class, path, key=None, **kwargs):
        """Retrieve from API endpoint that returns a list of items.

        Args:
            model (type): The type of object to build using the response from the API.
            path (str):   The path of API to send request to.
            key (str, optional): Key to use as index into each item of data from API.
            **kwargs:     Key-value pairs to include when making the request.

        Returns:
            list: A list containing items of type model_class.

        """
        url = posixpath.join(config.END_POINT, path)
        data = self.__get_data(url, kwargs)
        if not data:
            return None
        items = []
        for json_item in data:
            item = json_item[key] if key else json_item
            items.append(model_class(item, self))
        return items

    def __pager(self, model_class, path, count=20, page=1, **kwargs):
        """Paginate an API resource.

        This is a generator that yields a single result.
        It handles retrieving new pages from the Api as needed.

        Args:
            model_class (type): The type of model that will be instantiate for api results.
            path (str):         Path of API to send request to.
            count (int):        Number of Api items per page (Default value = 20).
            page (int):         The page to start the generator from (Default value = 1).
            **kwargs:           Key-value pairs to include when making the request.

        Yields:
            object: An instance of ``model_class``.

        """
        while True:
            items = self.__get_multiple(model_class, path, page=page, count=count, **kwargs)
            if items:
                for item in items:
                    yield item
                page += 1
            else:
                break

    def location(self, location_id, fields='all'):
        """Retrieve the episode corresponding to the specified id.

        Args:
            location_id (int): ID of the location to retrieve.

        Returns:
            Location: Location instance.

        """
        return self.__build_response("location.json?id={0}&fields={1}".format(location_id, fields), models.Location)

    def episodes(self, site=None, page=1, count=20):
        # TODO add more explanation about how iterable works (see shows() doc)
        """Get latest episodes from feed.

        Args:
            site (str, optional): If specified, only episodes from this site will be returned.
            page (int):           The page to start from (Default value = 1).
            count (int):          Number of Episodes per page (Default value = 20).

        Returns:
            iterable: An iterable collection of :class:`Episodes <rt_api.models.Episode>`
            from 'latest' feed.

        """
        return self.__pager(models.Episode, "feed/", key="item", type="Episode", count=count, page=page, site=site)

    def season(self, season_id):
        """Retrieve the season corresponding to the specified id.

        Args:
            season_id (int): ID of the season to retrieve.

        Returns:
            Season: Season instance.

        """
        return self.__build_response("seasons/{0}".format(season_id), models.Season)

    def season_episodes(self, season_id):
        """Retrieve the episodes that belong to the season with the specified id.

        Args:
            season_id (int): ID of the season.

        Returns:
            list: A list of :class:`~rt_api.models.Episode` objects.

        """
        res = []
        for episode in self.__pager(models.Episode, "seasons/{0}/episodes".format(season_id), count=20, page=1):
            res.append(episode)
        return res

    def show_seasons(self, show_id):
        """Get the seasons belonging to show with specified ID.

        Args:
            show_id (int): ID of the show.

        Returns:
            list: A list of :class:`~rt_api.models.Season` objects.

        """
        return self.__get_multiple(models.Season, "shows/{0}/seasons/".format(show_id))

    def shows(self, site=None, page=1, count=20):
        """Return an iterable feed of :class:`Shows <rt_api.models.Show>`.

        This will return an iterable, which starts at the specified page,
        and can be iterated over to retrieve all shows onwards.

        Under the hood, as this is iterated over, new pages are fetched from the API.
        Therefore, the size of ``count`` will dictate the delay this causes.

        A larger ``count`` means larger delay, but fewer total number of
        pages will need to be fetched.

        Args:
            site (str):  Only return shows from specified site, or all sites if None.
            page (int):  The page to start from (Default value = 1).
            count (int): Number of Shows per page (Default value = 20).

        Returns:
            iterable: An iterable collection of :class:`Shows <rt_api.models.Show>`.

        Example::

            r = rt_api()
            show_feed = r.shows(site="theKnow")
            for show in show_feed:
                print(show)

        """
        # TODO 'site' should be an Enum?
        return self.__pager(models.Show, "shows/", count=count, page=page, site=site)

    def search(self, query, include=None):
        """Perform a search for the specified query.

        Currently only supports searching for Episodes, Shows, and Users.
        Unfortunately, the Api only returns up to 10 of each resource type.

        Args:
            query (str): The value to search for.
            include (list, optional): A list of types to include in the results (Default value = None).
                If ``include`` is specified, only objects of those types will be returned in the results.

        Example:
            Search for "funny", only in shows and episodes.

            .. code-block::  python

                search("funny", include=[rt_api.models.Show, rt_api.models.Episode])

        Returns:
            list: The search results.

        """
        url = posixpath.join(config.END_POINT, "search/?q={0}".format(query))
        data = self.__get_data(url)
        mapping = {
            "episodes": models.Episode,
            "shows": models.Show,
            "users": models.User
        }
        items = []
        for result_set in data:
            # Try to find corresponding model for this result type
            model_key = None
            for result_type in mapping:
                if result_type in result_set.keys():
                    model_key = result_type
                    break
            if model_key:
                # Check if we are doing any filtering
                if include and mapping[model_key] not in include:
                    # This model is not in 'include', so skip it
                    continue
                for item in result_set[model_key]:
                    items.append(mapping[model_key](item))
        return items


class AuthenticationError(Exception):
    """Raised when an error is encountered while performing authentication."""

    pass


class NotAuthenticatedError(Exception):
    """Raised if an action requiring authentication is attempted but no account is authenticated."""

    pass