import json
from urllib.parse import urlparse

import click
from coreapi import Client
from coreapi import transports

from . import config_util


@click.group()
def client():
    pass

@click.group()
def config():
    pass

@click.command()
@click.argument('name')
@click.argument('value')
def set_config(name, value):
    """Set a configuration value.

    \b
    Configuration names include:
    - url: the URL of CloudLaunch server (e.g., https://beta.launch.usegalaxy.org)
    - token: an auth token for authenticating with the CloudLaunch API. See
      documentation for how to obtain an auth token
    """
    config_util.set_config_value(name, value)

@click.command()
def show_config():
    for name, value in config_util.get_config_values().items():
        print("{name}={value}".format(name=name, value=value))

@click.group()
def deployments():
    pass

@click.command()
@click.argument('name') # TODO: maybe default the name too, same as CloudLaunch UI?
@click.argument('application')
@click.argument('cloud')
@click.option('--application-version', help='Version of application to launch')
@click.option('--config-app', type=click.File('rb'), help='JSON application config file')
def create_deployment(name, application, cloud, application_version, config_app):
    # TODO: if application_version not specified then fetch the default version and use that instead
    # TODO: move coreapi Client instantiation to separate function
    auth_token = config_util.get_config_value("token")
    url = config_util.get_config_value("url")
    if not auth_token or not url:
        raise Exception("Auth token and url are required.")
    hostname = urlparse(url).netloc.split(":")[0]
    custom_transports = [
        transports.HTTPTransport(credentials={hostname: 'Token {}'.format(auth_token)})
    ]
    client = Client(transports=custom_transports)
    document = client.get('{url}/api/v1/schema/'.format(url=url))
    deploy_params = {
        'name': name,
        'application': application,
        'target_cloud': cloud,
        'application_version': application_version,
    }
    if config_app:
        deploy_params['config_app'] = json.loads(config_app.read())
    new_deployment = client.action(document, ['deployments', 'create'], params=deploy_params)
    print(new_deployment)

client.add_command(deployments)
client.add_command(config)

config.add_command(set_config, name='set')
config.add_command(show_config, name='show')

deployments.add_command(create_deployment, name='create')

if __name__ == '__main__':
    client()
