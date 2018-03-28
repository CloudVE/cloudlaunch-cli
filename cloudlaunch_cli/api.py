import abc
import copy
import sys
import types
from urllib.parse import urlparse

import coreapi


class APIConfig:
    """Config object with needed config values for accessing API."""
    def __init__(self, url, token):
        self.url = url
        self.token = token


class APIClient:

    # TODO: maybe configure routes/subroutes with dict of dicts?
    def __init__(self, url=None, token=None):
        # create config object from url and token
        config = APIConfig(url=url, token=token)
        self.deployments = Deployments(config)
        self.deployments.add_subroute('tasks', DeploymentTasks)
        self.auth = types.SimpleNamespace()
        self.auth.user = Users(config)
        self.auth.user.credentials = types.SimpleNamespace()
        self.auth.user.credentials.aws = AWSCredentials(config)
        self.auth.user.credentials.openstack = OpenstackCredentials(config)
        self.auth.user.credentials.azure = AzureCredentials(config)
        self.auth.user.credentials.gce = GCECredentials(config)


class APIResponse:
    """Represents response from CloudLaunch API.

    Response data dictionary can be accessed via the "data" attribute or
    directly on this instance.
    """

    def __init__(self, id, data=None, update_endpoint=None):
        self.id = id
        self.data = data
        self.update_endpoint = update_endpoint

    def update(self, **kwargs):
        """Update this instance, applying kwargs to data before updating."""
        if not self.update_endpoint:
            raise Exception("No endpoint for updating instance")
        data = copy.deepcopy(self.data)
        data.update(kwargs)
        # Remove 'id' item from data dict so it's not specified twice
        del data['id']
        api_response = self.update_endpoint.update(self.id, **data)
        self.data = api_response.data
        return api_response

    def partial_update(self, **kwargs):
        """Update this instance using the values specified in kwargs.

        NOTE: this doesn't apply any updates that have been made to the data
        attribute.
        """
        if not self.update_endpoint:
            raise Exception("No endpoint for updating instance")
        api_response = self.update_endpoint.partial_update(self.id, **kwargs)
        self.data = api_response.data
        return api_response

    def delete(self):
        """Delete this instance."""
        if not self.update_endpoint:
            raise Exception("No endpoint for deleting instance")
        self.update_endpoint.delete(self.id)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, key):
        return key in self.data


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
        """Get a resource and return an APIResponse."""
        pass

    @abc.abstractmethod
    def list(self, **kwargs):
        """Get a list of resources and return a list of APIResponses."""
        pass

    @abc.abstractmethod
    def create(self, **kwargs):
        """Create a resource and return an APIResponse."""
        pass

    @abc.abstractmethod
    def update(self, id, **kwargs):
        """Update a resource and return an APIResponse."""
        pass

    @abc.abstractmethod
    def partial_update(self, id, **kwargs):
        """Partially update a resource and return an APIResponse.

        For a partial update only the fields that are to be updated need be
        specified as kwargs.
        """
        pass

    @abc.abstractmethod
    def delete(self, id):
        """Delete a resource."""
        pass

    @abc.abstractmethod
    def add_subroute(self, name, child_endpoint):
        """Add a subroute to this endpoint.

        Adds an attribute with the given name of an instance of child_endpoint.
        Also will use this to create an instance of child_endpoint and add to
        each APIResponse returned, with the id of the APIResponse specified as
        the parent_id of the child_endpoint instance.
        """
        pass


class CoreAPIBasedAPIEndpoint(APIEndpoint):

    path = None
    subroutes = {}
    id_param_name = 'id'
    id_field_name = 'id'
    parent_url_kwarg = None

    def __init__(self, api_config, parent_id=None, parent_url_kwargs=None):
        self.api_config = api_config
        self.parent_url_kwargs = parent_url_kwargs if parent_url_kwargs else {}
        # TODO: maybe warn if parent_id is specified but not parent_url_kwarg
        if parent_id and self.parent_url_kwarg:
            self.parent_url_kwargs[self.parent_url_kwarg] = parent_id

    def get(self, id, **kwargs):
        document = self._create_client()
        params = kwargs if kwargs else {}
        params[self.id_param_name] = id
        if self.parent_url_kwargs:
            params.update(self.parent_url_kwargs)
        item = self._client.action(document, self.path + ['read'], params=params)
        return self._create_response(item)

    def list(self, **kwargs):
        document = self._create_client()
        params = kwargs if kwargs else {}
        if self.parent_url_kwargs:
            params.update(self.parent_url_kwargs)
        items = self._client.action(document, self.path + ['list'], params=params)
        # TODO: return a wrapper that supports pagination
        return [self._create_response(item) for item in items['results']]

    def create(self, **kwargs):
        document = self._create_client()
        params = kwargs if kwargs else {}
        if self.parent_url_kwargs:
            params.update(self.parent_url_kwargs)
        item = self._client.action(document, self.path + ['create'], params=params)
        return self._create_response(item)

    # TODO: update isn't working, params are added as url parameters?
    def update(self, id, **kwargs):
        document = self._create_client()
        params = kwargs if kwargs else {}
        params[self.id_param_name] = id
        if self.parent_url_kwargs:
            params.update(self.parent_url_kwargs)
        # Turn off validation for update since in general the params include all
        # of a resource's fields, including ones that are read-only
        item = self._client.action(document, self.path + ['update'], params=params, validate=False)
        return self._create_response(item)

    # TODO: partial_update isn't working, params are added as url parameters?
    def partial_update(self, id, **kwargs):
        document = self._create_client()
        params = kwargs if kwargs else {}
        params[self.id_param_name] = id
        if self.parent_url_kwargs:
            params.update(self.parent_url_kwargs)
        item = self._client.action(document, self.path + ['partial_update'], params=params)
        return self._create_response(item)

    def delete(self, id):
        document = self._create_client()
        params = {}
        params[self.id_param_name] = id
        if self.parent_url_kwargs:
            params.update(self.parent_url_kwargs)
        self._client.action(document, self.path + ['delete'], params=params)

    def add_subroute(self, name, child_endpoint):
        # TODO: maybe figure out the name from the paths?
        self.subroutes[name] = child_endpoint
        setattr(self, name, child_endpoint(self.api_config))

    def _create_response(self, data):
        object_id = data[self.id_field_name]
        api_response = APIResponse(id=object_id, data=data, update_endpoint=self)
        if self.subroutes:
            for k, v in self.subroutes.items():
                setattr(api_response, k, v(self.api_config, parent_id=object_id, parent_url_kwargs=self.parent_url_kwargs))
        # TODO: also add to response object update() and delete() methods
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


class Deployments(CoreAPIBasedAPIEndpoint):
    path = ['deployments']


class DeploymentTasks(CoreAPIBasedAPIEndpoint):
    path = ['deployments', 'tasks']
    parent_url_kwarg = 'deployment_pk'


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


# Temporary code for testing purposes
if __name__ == '__main__':
    url = sys.argv[1]
    token = sys.argv[2]
    api_client = APIClient(url=url, token=token)
    #deployments = api_client.deployments.list()
    #print([d.data for d in deployments])
    # deployment = api_client.deployments.get(deployments[0].data['id'])
    # print(deployment.data)
    # task = deployment.tasks.get(deployment.data['latest_task']['id'])
    # print(task.data)

    # Test creating
    # dep = api_client.deployments.create(
    #     name='my-ubuntu-test',
    #     application='ubuntu',
    #     target_cloud='amazon-us-east-n-virginia',
    #     application_version='16.04',
    #     config_app={
    #         'config_cloudlaunch': {
    #             'vmType': 't1.micro',
    #         }
    #     }
    # )
    # print(dep.data)

    # Test updating, not working currently
    # dep = api_client.deployments.get(23)
    # import json
    # print(json.dumps(dep.data, indent=True))
    # dep['archived'] = False
    # print(json.dumps(dep.data, indent=True))
    # dep.update()

    # Test updating
    # api_client.deployments.delete(19)
    # Test self-updating
    # dep = api_client.deployments.get(24)
    # dep.delete()

    # Test proxied dictionary access
    # dep = api_client.deployments.get(23)
    # print(dep['name'])
    # dep['name'] = 'updated-name'
    # print(dep['name'])
    # print('name' in dep)
    # print('foo' in dep)
    # print(dep['application_config']['config_cloudlaunch']['instanceType'])
