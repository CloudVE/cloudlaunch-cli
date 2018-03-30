import abc
from urllib.parse import urlparse

import coreapi

from . import resources


class APIEndpoint(metaclass=abc.ABCMeta):
    """Interface for CloudLaunch API endpoints."""

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


class CoreAPIBasedAPIEndpoint(APIEndpoint):

    path = None
    subroutes = {}
    id_param_name = 'id'
    id_field_name = 'id'
    parent_url_kwarg = None
    resource_type = resources.APIResource
    subroutes = {}

    def __init__(self, api_config, parent_id=None, parent_url_kwargs=None):
        self.api_config = api_config
        self.parent_url_kwargs = parent_url_kwargs if parent_url_kwargs else {}
        # TODO: maybe warn if parent_id is specified but not parent_url_kwarg
        if parent_id and self.parent_url_kwarg:
            self.parent_url_kwargs[self.parent_url_kwarg] = parent_id
        for name, child_endpoint in self.subroutes.items():
            setattr(self, name, child_endpoint(self.api_config))

    def get(self, id, **kwargs):
        document = self._create_client()
        params = kwargs if kwargs else {}
        params[self.id_param_name] = id
        if self.parent_url_kwargs:
            params.update(self.parent_url_kwargs)
        item = self._client.action(document, self.path + ['read'],
                                   params=params)
        return self._create_response(item)

    def list(self, **kwargs):
        document = self._create_client()
        params = kwargs if kwargs else {}
        if self.parent_url_kwargs:
            params.update(self.parent_url_kwargs)
        items = self._client.action(document, self.path + ['list'],
                                    params=params)
        # TODO: return a wrapper that supports pagination
        return [self._create_response(item) for item in items['results']]

    def create(self, **kwargs):
        document = self._create_client()
        params = kwargs if kwargs else {}
        if self.parent_url_kwargs:
            params.update(self.parent_url_kwargs)
        item = self._client.action(document, self.path + ['create'],
                                   params=params)
        return self._create_response(item)

    def update(self, id, **kwargs):
        document = self._create_client()
        params = kwargs if kwargs else {}
        params[self.id_param_name] = id
        if self.parent_url_kwargs:
            params.update(self.parent_url_kwargs)
        # Turn off validation for update since in general the params include
        # all of a resource's fields, including ones that are read-only
        item = self._client.action(document, self.path + ['update'],
                                   params=params, validate=False)
        return self._create_response(item)

    def partial_update(self, id, **kwargs):
        document = self._create_client()
        params = kwargs if kwargs else {}
        params[self.id_param_name] = id
        if self.parent_url_kwargs:
            params.update(self.parent_url_kwargs)
        item = self._client.action(document, self.path + ['partial_update'],
                                   params=params)
        return self._create_response(item)

    def delete(self, id):
        document = self._create_client()
        params = {}
        params[self.id_param_name] = id
        if self.parent_url_kwargs:
            params.update(self.parent_url_kwargs)
        self._client.action(document, self.path + ['delete'], params=params)

    def _create_response(self, data):
        object_id = data[self.id_field_name]
        api_response = self.resource_type(id=object_id, data=data,
                                          update_endpoint=self)
        if self.subroutes:
            for k, v in self.subroutes.items():
                setattr(api_response,
                        k,
                        v(self.api_config,
                          parent_id=object_id,
                          parent_url_kwargs=self.parent_url_kwargs))
        return api_response

    def _create_client(self):
        url = self.api_config.url
        auth_token = self.api_config.token
        if not auth_token or not url:
            raise Exception("Auth token and url are required.")
        hostname = urlparse(url).netloc.split(":")[0]
        custom_transports = [
            coreapi.transports.HTTPTransport(
                credentials={hostname: 'Token {}'.format(auth_token)})
        ]
        self._client = coreapi.Client(transports=custom_transports)
        return self._client.get('{url}/schema/'.format(url=url))


class DeploymentTasks(CoreAPIBasedAPIEndpoint):
    path = ['deployments', 'tasks']
    parent_url_kwarg = 'deployment_pk'
    resource_type = resources.Task


# TODO: update(), partial_update() don't work because 'archived' is added as
# query parameter
class Deployments(CoreAPIBasedAPIEndpoint):
    path = ['deployments']
    resource_type = resources.Deployment
    subroutes = {
        'tasks': DeploymentTasks
    }


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
