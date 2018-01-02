
import json
from urllib.parse import urlparse

import coreapi


class Client(object):

    def __init__(self, configuration):
        self.configuration = configuration

    def create_deployment(self, name, application, cloud, application_version, config_app=None):

        deploy_params = {
            'name': name,
            'application': application,
            'target_cloud': cloud,
            'application_version': application_version,
        }
        if config_app:
            deploy_params['config_app'] = json.loads(config_app.read())
        document = self._create_client()
        return self._client.action(document, ['deployments', 'create'], params=deploy_params)

    def _create_client(self):
        url = self.configuration.url
        auth_token = self.configuration.token
        if not auth_token or not url:
            raise Exception("Auth token and url are required.")
        hostname = urlparse(url).netloc.split(":")[0]
        custom_transports = [
            coreapi.transports.HTTPTransport(credentials={hostname: 'Token {}'.format(auth_token)})
        ]
        self._client = coreapi.Client(transports=custom_transports)
        return self._client.get('{url}/api/v1/schema/'.format(url=url))

