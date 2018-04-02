
import unittest

import coreapi

from cloudlaunch_cli.api import client, endpoints, resources


# Dummy classes created for testing CoreAPIBasedAPIEndpoint
class ParentResource(resources.APIResource):
    """Resource class for ParentEndpoint."""

    pass


class ChildResource(resources.APIResource):
    """Resource class for ChildEndpoint."""

    pass


class ChildEndpoint(endpoints.CoreAPIBasedAPIEndpoint):
    """Dummy ChildEndpoint class."""

    path = ['parent', 'child']
    parent_url_kwarg = 'parent_pk'
    resource_type = ChildResource


class ParentEndpoint(endpoints.CoreAPIBasedAPIEndpoint):
    """Dummy ParentEndpoint class."""

    path = ['parent']
    resource_type = ParentResource
    subroutes = {
        'child': ChildEndpoint
    }


class TestCoreAPIBasedAPIEndpoint(unittest.TestCase):
    """Tests for the CoreAPIBasedAPIEndpoint."""

    def setUp(self):
        self.coreapi_client_mock = unittest.mock.create_autospec(coreapi.Client, instance=True)
        self.coreapi_client_patcher = unittest.mock.patch('coreapi.Client', return_value=self.coreapi_client_mock)
        self.coreapi_client_patcher.start()
        self.addCleanup(self.coreapi_client_patcher.stop)
        self.config = client.APIConfig(url="http://localhost:8000/api/v1",
                                       token="abc123")
        self.parent_endpoint = ParentEndpoint(self.config)

    def test_get(self):
        """Test issuing 'get' request and returning instance."""
        document = {}

        self.coreapi_client_mock.configure_mock(**{
            'get.return_value': document,
            'action.return_value': {
                'id': 12,
                'name': 'parent-12'
            }
        })

        parent_12 = self.parent_endpoint.get(12)
        self.coreapi_client_mock.action.assert_called_with(
            document, ['parent', 'read'], params={'id': 12})
        # Verify ParentResource is created with 'child' subroute endpoint
        self.assertEqual(parent_12.id, 12)
        self.assertEqual(parent_12.name, 'parent-12')
        self.assertIsInstance(parent_12, ParentResource)
        self.assertIsInstance(parent_12.child, ChildEndpoint)
        self.assertEqual(parent_12.child.parent_url_kwargs, {
            'parent_pk': 12
        })
