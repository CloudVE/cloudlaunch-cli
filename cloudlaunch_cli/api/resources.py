import copy


class APIResource:
    """Wraps response from CloudLaunch API representing a resource."""

    _id = None
    _data = None
    _update_endpoint = None

    def __init__(self, id, data=None, update_endpoint=None):
        self._id = id
        self._update_endpoint = update_endpoint
        # Copy data so updates don't affect the passed in dict
        self._data = self.apply_data_mappings(copy.deepcopy(data))

    def apply_data_mappings(self, data):
        """Subclasses should apply necessary data mappings."""
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
        d = {}
        for k, v in self._data.items():
            if isinstance(v, APIResource):
                d[k] = v.asdict()
            else:
                d[k] = v
        return d


class Deployment(APIResource):

    def apply_data_mappings(self, data):
        data['launch_task'] = Task(data['launch_task']['id'],
                                   data=data['launch_task'],
                                   update_endpoint=self._update_endpoint.tasks)
        data['latest_task'] = Task(data['latest_task']['id'],
                                   data=data['latest_task'],
                                   update_endpoint=self._update_endpoint.tasks)
        return super().apply_data_mappings(data)

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


class Task(APIResource):

    @property
    def instance_status(self):
        """Return HEALTH_CHECK instance_status otherwise None."""
        if self.action == 'HEALTH_CHECK' and self.status == 'SUCCESS':
            return self.result['instance_status']
        else:
            return None
