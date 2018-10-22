import copy


class APIResource(object):
    """Wraps response from CloudLaunch API representing a resource."""

    id_field_name = 'id'
    # Data mappings ia dict of attribute names to callables that can be called
    # to convert attribute values into some type. The callable is assumed to
    # take only one argument.
    data_mappings = {}
    _id = None
    _data = None
    _update_endpoint = None

    def __init__(self, data=None):
        self._id = data.get(self.id_field_name)
        # Copy data so updates don't affect the passed in dict
        self._data = self._apply_data_mappings(copy.deepcopy(data))

    def _apply_data_mappings(self, data):
        """Subclasses should apply necessary data mappings."""
        for k, v in self.data_mappings.items():
            if k in data:
                if isinstance(data[k], list):
                    data[k] = [v(item) for item in data[k]]
                else:
                    data[k] = v(data[k])
        return data

    def update(self, **kwargs):
        """Update this instance, applying kwargs to data before updating."""
        if not self._update_endpoint:
            raise Exception("No endpoint for updating instance")
        data = self.asdict()
        data.update(kwargs)
        # Remove 'id' item from data dict so it's not specified twice
        del data['id']
        api_response = self._update_endpoint.update(self.id, **data)
        self._data = api_response._data
        return api_response

    def partial_update(self, **kwargs):
        """Update this instance using the values specified in kwargs.

        NOTE: this doesn't apply any updates that have been made to the data
        attribute.
        """
        if not self._update_endpoint:
            raise Exception("No endpoint for updating instance")
        api_response = self._update_endpoint.partial_update(self.id, **kwargs)
        self._data = api_response._data
        return api_response

    def delete(self):
        """Delete this instance."""
        if not self._update_endpoint:
            raise Exception("No endpoint for deleting instance")
        self._update_endpoint.delete(self.id)

    @property
    def id(self):
        """Return identifier of this resource."""
        return self._id

    def __getattr__(self, name):
        if name == '_data':
            raise AttributeError
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError

    def __setattr__(self, name, value):
        if not hasattr(APIResource, name) and hasattr(self, '_data'):
            self._data[name] = value
        else:
            object.__setattr__(self, name, value)

    def asdict(self):
        """Convert resource into data dictionary."""
        from . import endpoints
        d = {}
        for k, v in self._data.items():
            # Skip over subroute endpoint instances
            if isinstance(v, endpoints.APIEndpoint):
                continue
            if isinstance(v, APIResource):
                d[k] = v.asdict()
            else:
                d[k] = v
        return d

    def register_update_endpoint(self, update_endpoint):
        """Register endpoint for updating this resource and child resources."""
        self._update_endpoint = update_endpoint
        for name, mapped_type in self.data_mappings.items():
            attr = getattr(self, name)
            if isinstance(attr, APIResource):
                attr.register_update_endpoint(self.subroute_for(mapped_type))

    def subroute_for(self, resource_type):
        """Get a subroute of the update endpoint for given resource type."""
        return self._update_endpoint.subroutes(self.id).get(resource_type)


class Task(APIResource):

    @property
    def instance_status(self):
        """Return HEALTH_CHECK instance_status otherwise None."""
        if self.action == 'HEALTH_CHECK' and self.status == 'SUCCESS':
            return self.result['instance_status']
        else:
            return None


class Deployment(APIResource):

    data_mappings = {
        'launch_task': Task,
        'latest_task': Task,
    }

    @property
    def tasks(self):
        return self.subroute_for(Task)

    @property
    def public_ip(self):
        """Return public IP address of instance."""
        launch_task = self.launch_task
        if launch_task.result and 'cloudLaunch' in launch_task.result:
            return launch_task.result['cloudLaunch'].get('publicIP', None)
        else:
            return None

    def run_health_check(self):
        return self.tasks.create(action="HEALTH_CHECK")

    def run_restart(self):
        return self.tasks.create(action="RESTART")

    def run_delete(self):
        return self.tasks.create(action="DELETE")


class Cloud(APIResource):
    id_field_name = 'slug'


class Image(APIResource):
    pass


class ApplicationVersionCloudConfig(APIResource):

    data_mappings = {
        'cloud': Cloud,
        'image': Image,
    }


class ApplicationVersion(APIResource):
    data_mappings = {
        'cloud_config': ApplicationVersionCloudConfig
    }


class Application(APIResource):
    data_mappings = {
        'versions': ApplicationVersion
    }
    id_field_name = 'slug'
