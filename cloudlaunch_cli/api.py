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

    def __init__(self, id, data=None, parent=None):
        self.id = id
        self.data = data
        self.parent = parent


class APIEndpoint:

    path = None
    subroutes = {}
    parent_url_kwarg = None
    parent_endpoint = None

    def __init__(self, api_config, parent=None, parent_endpoint=None):
        self.api_config = api_config
        self.parent = parent
        self.parent_endpoint

    def get(self, id, **kwargs):
        document = self._create_client()
        params = kwargs if kwargs else {}
        params['id'] = id
        if self.parent:
            params.update(self._get_parent_url_kwargs(self.parent, self))
        resp = self._client.action(document, self.path + ['read'], params=params)
        api_response = APIResponse(id=id, data=resp, parent=self.parent)
        if self.subroutes:
            for k, v in self.subroutes.items():
                setattr(api_response, k, v(self.api_config, parent=api_response, parent_endpoint=self))
        return api_response

    def add_subroute(self, name, child_endpoint):
        # TODO: maybe figure out the name from the paths?
        self.subroutes[name] = child_endpoint
        setattr(self, name, child_endpoint(self.api_config))

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

    # TODO: resolve parent url kwargs when creating subroute endpoint instances
    # this way the subroute endpoint instances don't know anything about the data
    # don't technically need to know about parent_endpoint either???
    # - a endpoint could have parent_url_kwargs?
    def _get_parent_url_kwargs(self, parent_api_response, api_endpoint):
        kwargs = {}
        if parent_api_response:
            kwargs[api_endpoint.parent_url_kwarg] = parent_api_response.id
            if parent_api_response.parent:
                kwargs.update(self._get_parent_url_kwargs(parent_api_response, api_endpoint.parent_endpoint))
        return kwargs


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
    deployment = api_client.deployments.get(12)
    print(deployment.data)
    task = deployment.tasks.get(182)
    print(task.data)
