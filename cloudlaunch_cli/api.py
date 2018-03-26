import copy
import sys
from urllib.parse import urlparse

import coreapi


class APIConfig:
    def __init__(self, url=None, token=None):
        self.url = url
        self.token = token


class APIClient:

    # TODO: maybe configure routes/subroutes with dict of dicts?
    def __init__(self, url=None, token=None):
        # create config object from url and token
        config = APIConfig(url=url, token=token)
        self.deployments = Deployments(config)
        self.deployments.add_subroute('tasks', DeploymentTasks)


class APIResponse:

    def __init__(self, id, data=None, update_endpoint=None):
        self.id = id
        self.data = data
        self.update_endpoint = update_endpoint

    def update(self, **kwargs):
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
        if not self.update_endpoint:
            raise Exception("No endpoint for updating instance")
        api_response = self.update_endpoint.partial_update(self.id, **kwargs)
        self.data = api_response.data
        return api_response

    def delete(self):
        if not self.update_endpoint:
            raise Exception("No endpoint for deleting instance")
        self.update_endpoint.delete(self.id)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, key):
        return key in self.data


class APIEndpoint:

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
        item = self._client.action(document, self.path + ['update'], params=params)
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


class Deployments(APIEndpoint):
    path = ['deployments']


class DeploymentTasks(APIEndpoint):
    path = ['deployments', 'tasks']
    parent_url_kwarg = 'deployment_pk'


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
