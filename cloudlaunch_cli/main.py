import json

import arrow
import click

from .api.client import APIClient
from .api.cloud_credentials import CloudCredentials
from .config import Configuration

conf = Configuration()

cli_context = {}


def create_api_client(cloud=None, cloud_credentials_json=None):

    cloudlaunch_client = APIClient(url=conf.url, token=conf.token)
    # Recreate client with cloud credentials if available
    if cloud:
        cloud_resource = cloudlaunch_client.infrastructure.clouds.get(cloud)
        # Try to load if specified on command line first, then look in
        # environment variables
        if 'cloud-credentials' in cli_context:
            creds_dict = json.loads(cli_context['cloud-credentials'].read())
            cloud_creds = CloudCredentials.load_from_dict(
                cloud_resource.resourcetype, creds_dict)
        else:
            cloud_creds = CloudCredentials.load_from_environment(
                cloud_resource.resourcetype)
        if cloud_creds:
            return APIClient(url=conf.url, token=conf.token,
                             cloud_credentials=cloud_creds)
    return cloudlaunch_client


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
      (e.g., https://launch.usegalaxy.org/cloudlaunch/api/v1)
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
@click.option('--cloud-credentials', type=click.File('rb'),
              help="JSON file with cloud credentials.")
def deployments(cloud_credentials):
    """Manage CloudLaunch deployments.

    You can pass cloud credentials either as environment variables or as a JSON
    file.
    TODO: document the expected names of variables.
    """
    global cli_context
    if cloud_credentials:
        cli_context['cloud-credentials'] = cloud_credentials


@click.command()
# TODO: maybe default the name too, same as CloudLaunch UI?
@click.argument('name')
@click.argument('application')
@click.argument('cloud')
@click.argument('target_id')
@click.option('--application-version', help='Version of application to launch')
@click.option('--config-app', type=click.File('rb'),
              help='JSON application config file')
def create_deployment(name, application, cloud, target_id, application_version,
                      config_app):
    # TODO: if application_version not specified then fetch the default version
    # and use that instead
    config_app = json.loads(config_app.read()) if config_app else None
    cloudlaunch_client = create_api_client(cloud)
    params = {
        'name': name,
        'application': application,
        'deployment_target_id': target_id,
        'application_version': application_version
    }
    if config_app:
        params['config_app'] = config_app
    new_deployment = cloudlaunch_client.deployments.create(**params)
    _print_deployments([new_deployment])


@click.command()
@click.option('--archived', is_flag=True,
              help='Show only archived deployments')
def list_deployments(archived):
    deployments = create_api_client().deployments.list(archived=archived)
    _print_deployments(deployments)


def _print_deployments(deployments):
    if len(deployments) > 0:
        print("{:6s}  {:24s}  {:6s}  {:15s}  {:20s}  {:15s}".format(
            "ID", "Name", "Cloud", "Created", "Status", "Address"))
    else:
        print("No deployments.")
    for deployment in deployments:
        created_date = arrow.get(deployment.added)
        latest_task = deployment.latest_task
        latest_task_status = latest_task.instance_status \
            if latest_task.instance_status else latest_task.status
        latest_task_display = "{action}:{latest_task_status}".format(
            action=latest_task.action,
            latest_task_status=latest_task_status)
        ip_address = deployment.public_ip if deployment.public_ip else 'N/A'
        cloud = deployment._data['deployment_target']['target_zone']['cloud']['id']
        print("{identifier:6d}  {name:24.24s}  {cloud:6.6s}  {created_date:15.15s}  "
              "{latest_task_display:20.20s}  {ip_address:15.15s}".format(
                  identifier=deployment._id, cloud=cloud,
                  created_date=created_date.humanize(),
                  latest_task_display=latest_task_display,
                  ip_address=ip_address, **deployment._data))


@click.group()
def applications():
    pass


@click.command()
# TODO: maybe default the name too, same as CloudLaunch UI?
@click.argument('name')
@click.argument('summary')
@click.option('--maintainer', help='Maintainer of app')
@click.option('--description', help='Description of app')
def create_application(name, summary, maintainer, description):
    new_app = create_api_client().applications.create(
        name=name, summary=summary, maintainer=maintainer,
        description=description)
    _print_applications([new_app])


@click.command()
def list_applications():
    applications = create_api_client().applications.list()
    _print_applications(applications)


def _print_applications(applications):
    if len(applications) > 0:
        print("{:24s}  {:15s}  {:20s}  {:15s}".format(
            "Name", "Created Date", "Maintainer", "Summary"))
    else:
        print("No applications found.")
    for app in applications:
        created_date = arrow.get(app.added)
        print("{name:24.24s}  {created_date:15.15s}  "
              "{maintainer!s:20.20}  {summary!s:30.30}".format(
                  created_date=created_date.humanize(),
                  **app._data))


@click.group()
@click.pass_context
def clouds(ctx):
    ctx.obj = ctx.obj or {}


@clouds.group()
@click.option('--cloud_id', help='Cloud ID')
@click.pass_context
def regions(ctx, cloud_id):
    ctx.obj['cloud_id'] = cloud_id


@regions.command(name='list')
@click.pass_context
def list_regions(ctx):
    cloud = create_api_client().infrastructure.clouds.get(ctx.obj['cloud_id'])
    _print_regions(cloud.regions.list())


@regions.group()
@click.option('--region_id', help='Region ID')
@click.pass_context
def zones(ctx, region_id):
    ctx.obj['region_id'] = region_id


@zones.group()
@click.option('--zone_id', help='Zone ID')
@click.pass_context
def compute(ctx, zone_id):
    ctx.obj['zone_id'] = zone_id


@compute.group()
@click.pass_context
def vm_types(ctx):
    pass


@vm_types.command(name='list')
@click.option('--min_vcpus', help='Min CPUs', default=0)
@click.option('--min_ram', help='Min RAM', default=0)
@click.option('--prefix', help='Prefix of instance family', default="")
@click.pass_context
def list_vm_types(ctx, min_vcpus, min_ram, prefix):
    cloud = create_api_client().infrastructure.clouds.get(ctx.obj['cloud_id'])
    region = cloud.regions.get(ctx.obj['region_id'])
    zone = region.zones.get(ctx.obj['zone_id'])
    _print_vm_types(zone.vm_types.list(min_vcpus=min_vcpus, min_ram=min_ram, vm_type_prefix=prefix))


@zones.command(name='list')
@click.pass_context
def list_zones(ctx):
    cloud = create_api_client().infrastructure.clouds.get(ctx.obj['cloud_id'])
    region = cloud.regions.get(ctx.obj['region_id'])
    _print_zones(region.zones.list())


@click.command()
def list_clouds():
    clouds = create_api_client().infrastructure.clouds.list()
    _print_clouds(clouds)


def _print_clouds(clouds):
    id_width = max([len(cloud.id) for cloud in clouds]) + 1
    if len(clouds) > 0:
        header_format = "{{:{id_width!s}s}} {{:30s}} {{:20s}}"\
                        .format(id_width=id_width)
        print(header_format.format(
            "Id", "Name", "Cloud Type"))
    else:
        print("No clouds found.")
    row_format = "{{id:{id_width!s}.{id_width!s}s}} {{name:30.30s}} "\
                 "{{resourcetype:20.20}}"\
                 .format(id_width=id_width)
    for cloud in clouds:
        print(row_format.format(**cloud.asdict()))


def _print_regions(regions):
    id_width = max([len(region.id) for region in regions]) + 1
    if len(regions) > 0:
        header_format = "{{:{id_width!s}s}} {{:30s}}"\
                        .format(id_width=id_width)
        print(header_format.format(
            "Id", "Name"))
    else:
        print("No regions found.")
    row_format = "{{region_id:{id_width!s}.{id_width!s}s}} {{name:30.30s}}" \
                 .format(id_width=id_width)
    for region in regions:
        print(row_format.format(**region.asdict()))


def _print_zones(zones):
    id_width = max([len(zone.id) for zone in zones]) + 1
    if len(zones) > 0:
        header_format = "{{:{id_width!s}s}} {{:30s}}"\
                        .format(id_width=id_width)
        print(header_format.format(
            "Id", "Name"))
    else:
        print("No zones found.")
    row_format = "{{zone_id:{id_width!s}.{id_width!s}s}} {{name}}" \
                 .format(id_width=id_width)
    for zone in zones:
        print(row_format.format(**zone.asdict()))


def _print_vm_types(vm_types):
    id_width = max([len(vm_type.id) for vm_type in vm_types]) + 1
    if len(vm_types) > 0:
        header_format = "{{:{id_width!s}s}} {{:30s}} {{:20s}} {{:20s}}"\
                        .format(id_width=id_width)
        print(header_format.format(
            "Id", "Name", "CPUs", "RAM"))
    else:
        print("No vm types found.")
    row_format = "{{id:{id_width!s}.{id_width!s}s}} {{name:30.30s}} {{vcpus:20.20s}} {{ram:20.20s}}" \
                 .format(id_width=id_width)
    for vm_type in vm_types:
        print(row_format.format(**vm_type.asdict()))


client.add_command(deployments)
client.add_command(applications)
client.add_command(clouds)
client.add_command(config)

config.add_command(set_config, name='set')
config.add_command(show_config, name='show')

deployments.add_command(create_deployment, name='create')
deployments.add_command(list_deployments, name='list')

applications.add_command(create_application, name='create')
applications.add_command(list_applications, name='list')

clouds.add_command(list_clouds, name='list')

if __name__ == '__main__':
    client()
