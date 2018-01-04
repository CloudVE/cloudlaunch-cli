import arrow
import click

from .client import CloudLaunchClient
from .config import Configuration

conf = Configuration()
cloudlaunch_client = CloudLaunchClient(conf)


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
    - url: the URL of CloudLaunch server
      (e.g., https://beta.launch.usegalaxy.org/cloudlaunch/api/v1)
    - token: an auth token for authenticating with the CloudLaunch API. See
      documentation for how to obtain an auth token
    """
    if name not in dir(conf):
        raise click.BadParameter("{name} is not a recognized "
                                 "config parameter".format(name=name))
    try:
        setattr(conf, name, value)
    except Exception as e:
        raise click.BadParameter("Unable to set {name}: {error}".format(
            name=name, error=e))


@click.command()
def show_config():
    for name, value in conf.asdict().items():
        print("{name}={value}".format(name=name, value=value))


@click.group()
def deployments():
    pass


@click.command()
# TODO: maybe default the name too, same as CloudLaunch UI?
@click.argument('name')
@click.argument('application')
@click.argument('cloud')
@click.option('--application-version', help='Version of application to launch')
@click.option('--config-app', type=click.File('rb'),
              help='JSON application config file')
def create_deployment(name, application, cloud, application_version,
                      config_app):
    # TODO: if application_version not specified then fetch the default version
    # and use that instead
    new_deployment = cloudlaunch_client.create_deployment(
        name, application, cloud, application_version, config_app)
    _print_deployments([new_deployment])


@click.command()
@click.option('--archived', is_flag=True,
              help='Show only archived deployments')
def list_deployments(archived):
    deployments = cloudlaunch_client.list_deployments(archived=archived)
    _print_deployments(deployments['results'])


def _print_deployments(deployments):
    if len(deployments) > 0:
        print("{:24s}  {:15s}  {:20s}  {:15s}".format(
            "Name", "Created", "Status", "Address"))
    else:
        print("No deployments.")
    for deployment in deployments:
        created_date = arrow.get(deployment['added'])
        latest_task = deployment['latest_task']
        latest_task_status = latest_task['status']
        if latest_task['action'] == 'HEALTH_CHECK' \
                and latest_task['status'] == 'SUCCESS':
            latest_task_status = latest_task['result']['instance_status']
        latest_task_display = "{action}:{latest_task_status}".format(
            action=latest_task['action'],
            latest_task_status=latest_task_status)
        ip_address = 'N/A'
        launch_task = deployment['launch_task']
        if 'cloudLaunch' in launch_task['result']:
            ip_address = launch_task['result']['cloudLaunch']['publicIP']
        print("{name:24.24s}  {created_date:15.15s}  "
              "{latest_task_display:20.20s}  {ip_address:15.15s}".format(
                  created_date=created_date.humanize(),
                  latest_task_display=latest_task_display,
                  ip_address=ip_address, **deployment))


client.add_command(deployments)
client.add_command(config)

config.add_command(set_config, name='set')
config.add_command(show_config, name='show')

deployments.add_command(create_deployment, name='create')
deployments.add_command(list_deployments, name='list')

if __name__ == '__main__':
    client()
