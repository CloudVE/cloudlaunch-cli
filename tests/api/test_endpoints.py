
import unittest
import unittest.mock

from cloudlaunch_cli.api import client, endpoints, resources

import coreapi


# Dummy classes created for testing CoreAPIBasedAPIEndpoint
class ParentResource(resources.APIResource):
    """Resource class for ParentEndpoint."""

    @property
    def child(self):
        return self.subroute_for(ChildResource)


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

    @property
    def child(self):
        return ChildEndpoint(self.api_config)


class TestCoreAPIBasedAPIEndpoint(unittest.TestCase):
    """Tests for the CoreAPIBasedAPIEndpoint."""

    def setUp(self):
        self.coreapi_client_mock = unittest.mock.create_autospec(
            coreapi.Client, instance=True)
        self.coreapi_client_patcher = unittest.mock.patch(
            'coreapi.Client', return_value=self.coreapi_client_mock)
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
        self._assertParentResourceEqual(
            parent_12, ParentResource(data={'id': 12, 'name': 'parent-12'}))
        self.assertIsInstance(parent_12.child, ChildEndpoint)
        self.assertEqual(parent_12.child.parent_url_kwargs, {
            'parent_pk': 12
        })

    def test_get_with_parent_url_kwarg(self):
        """Test issuing 'get' request for subroute instance with a parent."""
        child_endpoint = ChildEndpoint(self.config, parent_id=12)

        document = {}
        self.coreapi_client_mock.configure_mock(**{
            'get.return_value': document,
            'action.return_value': {
                'id': 22,
                'name': 'child-22'
            }
        })

        child_22 = child_endpoint.get(22)
        self.coreapi_client_mock.action.assert_called_with(
            document, ['parent', 'child', 'read'], params={
                'id': 22,
                'parent_pk': 12
            }
        )
        self.assertEqual(child_22.id, 22)
        self.assertEqual(child_22.name, 'child-22')
        self.assertIsInstance(child_22, ChildResource)

    def test_get_with_init_parent_url_kwargs(self):
        """Test 'get' for subroute with parent and parent_url_kwargs."""
        # In this contrived example the child's parent itself has a parent
        # hence the 'parent_parent_pk'
        child_endpoint = ChildEndpoint(self.config, parent_id=12,
                                       parent_url_kwargs={
                                           'parent_parent_pk': 33
                                       })

        document = {}
        self.coreapi_client_mock.configure_mock(**{
            'get.return_value': document,
            'action.return_value': {
                'id': 22,
                'name': 'child-22'
            }
        })

        child_endpoint.get(22)
        self.coreapi_client_mock.action.assert_called_with(
            document, ['parent', 'child', 'read'], params={
                'id': 22,
                'parent_pk': 12,
                'parent_parent_pk': 33,
            }
        )

    def test_list(self):
        """Test 'list' request that returns paged results."""
        document = {}

        # Simulate returning paged results
        self.coreapi_client_mock.configure_mock(**{
            'get.return_value': document,
            'action.return_value': {
                'count': 3,
                'next': None,
                'previous': None,
                'results': [{
                    'id': 12,
                    'name': 'parent-12'
                }, {
                    'id': 201,
                    'name': 'parent-201'
                }, {
                    'id': 202,
                    'name': 'parent-202'
                }]
            }
        })

        parents = self.parent_endpoint.list(deleted=True)
        self.coreapi_client_mock.action.assert_called_with(
            document, ['parent', 'list'], params={'deleted': True})
        # Verify ParentResource list
        self.assertEqual(len(parents), 3)
        for parent in parents:
            self._assertParentResourceEqual(
                parent, ParentResource(data={'id': parent.id, 'name': parent.name}))
            self.assertEqual(parent.child.parent_url_kwargs, {
                'parent_pk': parent.id
            })

    def test_create(self):
        """Test 'create' method."""
        document = {}

        # Simulate returning paged results
        self.coreapi_client_mock.configure_mock(**{
            'get.return_value': document,
            'action.return_value': {
                'id': 12,
                'name': 'parent-12'
            }
        })

        parent = self.parent_endpoint.create(name='parent-12')
        self.coreapi_client_mock.action.assert_called_with(
            document, ['parent', 'create'], params={'name': 'parent-12'})
        # Verify ParentResource list
        self._assertParentResourceEqual(
            parent, ParentResource(data={'id': 12, 'name': 'parent-12'}))

    def test_update(self):
        """Test 'update' method."""
        document = {}

        # Simulate returning paged results
        self.coreapi_client_mock.configure_mock(**{
            'get.return_value': document,
            'action.return_value': {
                'id': 12,
                'name': 'updated-name'
            }
        })

        parent = self.parent_endpoint.update(id=12, name='updated-name')
        self.coreapi_client_mock.action.assert_called_with(
            document, ['parent', 'update'],
            params={'id': 12, 'name': 'updated-name'}, validate=False)
        # Verify ParentResource list
        self._assertParentResourceEqual(
            parent, ParentResource(data={'id': 12, 'name': 'updated-name'}))

    def test_update_on_resource_instance(self):
        """Test 'update' when called on resource instance."""
        document = {}

        self.coreapi_client_mock.configure_mock(**{
            'get.return_value': document,
            'action.return_value': {
                'id': 12,
                'name': 'parent-12',
                'email': 'support@example.com'
            }
        })

        parent_12 = self.parent_endpoint.get(12)
        self.coreapi_client_mock.action.assert_called_with(
            document, ['parent', 'read'], params={'id': 12})

        self.coreapi_client_mock.configure_mock(**{
            'get.return_value': document,
            'action.return_value': {
                'id': 12,
                'name': 'parent-12',
                'email': 'updated@example.com'
            }
        })
        updated_parent_12 = parent_12.update(email='updated@example.com')
        self.coreapi_client_mock.action.assert_called_with(
            document, ['parent', 'update'],
            params={
                'id': 12, 'name': 'parent-12', 'email': 'updated@example.com'
            },
            validate=False)

    def test_partial_update(self):
        """Test 'partial_update' request."""
        document = {}

        # Simulate returning paged results
        self.coreapi_client_mock.configure_mock(**{
            'get.return_value': document,
            'action.return_value': {
                'id': 12,
                'name': 'updated-name',
                'email': 'support@example.com',
            }
        })

        parent = self.parent_endpoint.partial_update(12, name='updated-name')
        self.coreapi_client_mock.action.assert_called_with(
            document, ['parent', 'partial_update'],
            params={'id': 12, 'name': 'updated-name'})
        # Verify ParentResource list
        self._assertParentResourceEqual(
            parent, ParentResource(data={
                'id': 12,
                'name': 'updated-name',
                'email': 'support@example.com'
            }))

    def test_delete(self):
        """Test 'delete' method."""
        document = {}

        # Simulate returning paged results
        self.coreapi_client_mock.configure_mock(**{
            'get.return_value': document,
            'action.return_value': {
                'id': 12,
                'name': 'updated-name',
                'email': 'support@example.com',
            }
        })

        self.parent_endpoint.delete(12)
        self.coreapi_client_mock.action.assert_called_with(
            document, ['parent', 'delete'], params={'id': 12})

    def _assertParentResourceEqual(self, a, b):
        self.assertIsInstance(a, ParentResource)
        self.assertIsInstance(b, ParentResource)
        self.assertEqual(a.id, b.id)
        self.assertEqual(a.name, b.name)
