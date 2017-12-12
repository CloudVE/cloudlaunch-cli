
import click
from coreapi import Client
from coreapi import transports


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
    # TODO: implement
    pass

@click.command()
def show_config():
    # TODO: implement
    pass

@click.group()
def deployments():
    pass

@click.command()
@click.argument('name') # TODO: maybe default the name too, same as CloudLaunch UI?
@click.argument('application')
@click.argument('cloud')
@click.option('--application-version', help='Version of application to launch')
@click.option('--app-config', type=click.File('rb'), help='JSON application config file')
def create_deployment(name, application, cloud, application_version, app_config):
    # TODO: if application_version not specified then fetch the default version and use that instead
    # TODO: load token and URL from config
    # TODO: move coreapi Client instantiation to separate function
    auth_token = ''
    custom_transports = [
        transports.HTTPTransport(credentials={'localhost': 'Token {}'.format(auth_token)})
    ]
    client = Client(transports=custom_transports)
    document = client.get('http://localhost:8000/api/v1/schema/')
    new_deployment = client.action(document, ['deployments', 'create'], params={
        'name': name,
        'application': application,
        'target_cloud': cloud,
        'application_version': application_version,
    })
    print(new_deployment)

client.add_command(deployments)
client.add_command(config)

config.add_command(set_config, name='set')
config.add_command(show_config, name='show')

deployments.add_command(create_deployment, name='create')

if __name__ == '__main__':
    client()
