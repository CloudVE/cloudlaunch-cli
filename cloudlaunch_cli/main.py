import click

from .client import Client
from .config import Configuration

conf = Configuration()


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
    if name not in dir(conf):
        raise click.BadParameter("{name} is not a recognized config parameter".format(name=name))
    setattr(conf, name, value)

@click.command()
def show_config():
    for name, value in conf.asdict().items():
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
    client = Client(conf)
    new_deployment = client.create_deployment(name, application, cloud, application_version, config_app)
    print(new_deployment)

client.add_command(deployments)
client.add_command(config)

config.add_command(set_config, name='set')
config.add_command(show_config, name='show')

deployments.add_command(create_deployment, name='create')

if __name__ == '__main__':
    client()
