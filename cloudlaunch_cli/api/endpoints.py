import abc

try:
    from urllib.parse import urlparse
except ImportError:  # python 2
    from urlparse import urlparse

import coreapi

from . import resources


class APIEndpoint(object):
    """Interface for CloudLaunch API endpoints."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, api_config, parent_id=None, parent_url_kwargs=None):
        """Create API Endpoint instance.

        Arguments:
        api_config -- APIConfig instance

        Keyword arguments:
        parent_id -- for instances of subroutes that have a parent resource,
                     this is the id of that parent
        parent_url_kwargs -- for instances of subroutes that have a parent
                             resource, a dictionary of that parent resource's
                             url kwargs
        """
        pass

    @abc.abstractmethod
    def get(self, id, **kwargs):
        """Get a resource and return an APIResource."""
        pass

    @abc.abstractmethod
    def list(self, **kwargs):
        """Get a list of resources and return a list of APIResources."""
        pass

    @abc.abstractmethod
    def create(self, **kwargs):
        """Create a resource and return an APIResource."""
        pass

    @abc.abstractmethod
    def update(self, id, **kwargs):
        """Update a resource and return an APIResource."""
        pass

    @abc.abstractmethod
    def partial_update(self, id, **kwargs):
        """Update partially a resource and return an APIResource.

        For a partial update only the fields that are to be updated need be
        specified as kwargs.
        """
        pass

    @abc.abstractmethod
    def delete(self, id):
        """Delete a resource."""
        pass

    @abc.abstractmethod
    def subroutes(self, id):
        """Create subroute endpoint instances for the given id.

        Returns a dict with APIResource types as keys and APIEndpoint instances
        as keys.
        """
        pass


class CoreAPIBasedAPIEndpoint(APIEndpoint):

    path = None
    id_param_name = 'id'
    parent_url_kwarg = None
    resource_type = resources.APIResource
    _subroute_types = None

    def __init__(self, api_config, parent_id=None, parent_url_kwargs=None):
        self.api_config = api_config
        self.parent_url_kwargs = parent_url_kwargs if parent_url_kwargs else {}
        # TODO: maybe warn if parent_id is specified but not parent_url_kwarg
        if parent_id and self.parent_url_kwarg:
            self.parent_url_kwargs[self.parent_url_kwarg] = parent_id

    def get(self, id, **kwargs):
        document = self._create_client()
        params = self._create_params(id=id, **kwargs)
        item = self._client.action(document, self.path + ['read'],
                                   params=params)
        return self._create_response(item)

    def list(self, **kwargs):
        document = self._create_client()
        params = self._create_params(**kwargs)
        items = self._client.action(document, self.path + ['list'],
                                    params=params)
        # TODO: return a wrapper that supports pagination
        return [self._create_response(item) for item in items['results']]

    def create(self, **kwargs):
        document = self._create_client()
        params = self._create_params(**kwargs)
        item = self._client.action(document, self.path + ['create'],
                                   params=params)
        return self._create_response(item)

    def update(self, id, **kwargs):
        document = self._create_client()
        params = self._create_params(id=id, **kwargs)
        # Turn off validation for update since in general the params include
        # all of a resource's fields, including ones that are read-only
        item = self._client.action(document, self.path + ['update'],
                                   params=params, validate=False)
        return self._create_response(item)

    def partial_update(self, id, **kwargs):
        document = self._create_client()
        params = self._create_params(id=id, **kwargs)
        item = self._client.action(document, self.path + ['partial_update'],
                                   params=params)
        return self._create_response(item)

    def delete(self, id):
        document = self._create_client()
        params = self._create_params(id=id)
        self._client.action(document, self.path + ['delete'], params=params)

    def subroutes(self, id):
        # Assume that attributes that are APIEndpoint instances are subroutes
        if not self._subroute_types:
            self._subroute_types = {}
            for name in dir(self):
                val = getattr(self, name)
                if isinstance(val, APIEndpoint):
                    self._subroute_types[val.resource_type] = val.__class__
        subroutes = {}
        for resource_type, endpoint_type in self._subroute_types.items():
            subroutes[resource_type] = endpoint_type(
                self.api_config,
                parent_id=id,
                parent_url_kwargs=self.parent_url_kwargs)
        return subroutes

    def _create_params(self, id=None, **kwargs):
        params = kwargs if kwargs else {}
        if id:
            params[self.id_param_name] = id
        if self.parent_url_kwargs:
            params.update(self.parent_url_kwargs)
        return params

    def _create_response(self, data):
        api_response = self.resource_type(data)
        api_response.register_update_endpoint(self)
        return api_response

    def _create_client(self):
        url = self.api_config.url
        auth_token = self.api_config.token
        if not auth_token or not url:
            raise Exception("Auth token and url are required.")
        hostname = urlparse(url).netloc.split(":")[0]
        http_headers = {}
        if self.api_config.cloud_credentials:
            http_headers = self.api_config.cloud_credentials.to_http_headers()
        custom_transports = [
            coreapi.transports.HTTPTransport(
                credentials={hostname: 'Token {}'.format(auth_token)},
                headers=http_headers)
        ]
        self._client = coreapi.Client(transports=custom_transports)
        url = url if url and url.endswith("/") else url + "/"
        return self._client.get('{url}schema/'.format(url=url))


class DeploymentTasks(CoreAPIBasedAPIEndpoint):
    path = ['deployments', 'tasks']
    parent_url_kwarg = 'deployment_pk'
    resource_type = resources.Task


# TODO: update(), partial_update() don't work because 'archived' is added as
# query parameter
class Deployments(CoreAPIBasedAPIEndpoint):
    path = ['deployments']
    resource_type = resources.Deployment
    _tasks = None

    @property
    def tasks(self):
        if not self._tasks:
            self._tasks = DeploymentTasks(self.api_config)
        return self._tasks


class Users(CoreAPIBasedAPIEndpoint):
    path = ['auth', 'user']


class AWSCredentials(CoreAPIBasedAPIEndpoint):
    path = ['auth', 'user', 'credentials', 'aws']


class OpenstackCredentials(CoreAPIBasedAPIEndpoint):
    path = ['auth', 'user', 'credentials', 'openstack']


class AzureCredentials(CoreAPIBasedAPIEndpoint):
    path = ['auth', 'user', 'credentials', 'azure']


class GCECredentials(CoreAPIBasedAPIEndpoint):
    path = ['auth', 'user', 'credentials', 'gce']


class Applications(CoreAPIBasedAPIEndpoint):
    path = ['applications']
    resource_type = resources.Application
    id_param_name = 'slug'


class Clouds(CoreAPIBasedAPIEndpoint):
    path = ['infrastructure', 'clouds']
    resource_type = resources.Cloud
    id_param_name = 'slug'
