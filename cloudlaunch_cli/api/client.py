try:
    from types import SimpleNamespace
except: # Python 2
    from argparse import Namespace as SimpleNamespace

from . import endpoints


class APIConfig:
    """Config object with needed config values for accessing API."""
    def __init__(self, url, token, cloud_credentials=None):
        self.url = url
        self.token = token
        # cloud_credentials is a dict
        self.cloud_credentials = cloud_credentials


class APIClient:

    def __init__(self, url=None, token=None, cloud_credentials=None):
        # create config object from url and token (and optionally, credentials)
        config = APIConfig(url=url, token=token,
                           cloud_credentials=cloud_credentials)
        self.deployments = endpoints.Deployments(config)
        self.applications = endpoints.Applications(config)
        self.auth = SimpleNamespace()
        self.auth.user = endpoints.Users(config)
        credentials = SimpleNamespace()
        credentials.aws = endpoints.AWSCredentials(config)
        credentials.openstack = endpoints.OpenstackCredentials(config)
        credentials.azure = endpoints.AzureCredentials(config)
        credentials.gce = endpoints.GCECredentials(config)
        self.auth.user.credentials = credentials
        self.infrastructure = SimpleNamespace()
        self.infrastructure.clouds = endpoints.Clouds(config)


# For testing purposes only
if __name__ == '__main__':
    from http.client import HTTPConnection
    HTTPConnection.debuglevel = 1

    import logging
    # you need to initialize logging, otherwise you will not see anything from
    # requests
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    import sys
    url = sys.argv[1]
    token = sys.argv[2]
    api_client = APIClient(url=url, token=token)
    # deployments = api_client.deployments.list()
    # print([d.data for d in deployments])
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
    # print(dep.id)

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
    # dep['archived'] = False
    # dep.update()
    # import json
    # print(json.dumps(dep.data, indent=True))
    # print(dep['application_config']['config_cloudlaunch']['instanceType'])

    # Test AWSCredentials
    import json
    aws_creds = api_client.auth.user.credentials.aws.list()
    print(json.dumps([(aws_cred.name, aws_cred.access_key) for aws_cred in aws_creds], indent=True))
