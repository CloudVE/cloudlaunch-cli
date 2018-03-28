import copy


class APIResource:
    """Wraps response from CloudLaunch API representing a resource."""

    def __init__(self, id, data=None, update_endpoint=None):
        self._id = id
        self._data = data
        self._update_endpoint = update_endpoint

    def update(self, **kwargs):
        """Update this instance, applying kwargs to data before updating."""
        if not self._update_endpoint:
            raise Exception("No endpoint for updating instance")
        data = copy.deepcopy(self._data)
        data.update(kwargs)
        # Remove 'id' item from data dict so it's not specified twice
        del data['id']
        api_response = self._update_endpoint.update(self.id, **data)
        self.data = api_response.data
        return api_response

    def partial_update(self, **kwargs):
        """Update this instance using the values specified in kwargs.

        NOTE: this doesn't apply any updates that have been made to the data
        attribute.
        """
        if not self._update_endpoint:
            raise Exception("No endpoint for updating instance")
        api_response = self._update_endpoint.partial_update(self.id, **kwargs)
        self._data = api_response.data
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
        if not hasattr(self, name) and hasattr(self, '_data'):
            self._data[name] = value
        else:
            object.__setattr__(self, name, value)
