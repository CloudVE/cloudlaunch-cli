
import copy
import json
import unittest
from unittest.mock import Mock

from cloudlaunch_cli.api import client, endpoints, resources

from tests import load_fixture


class TestDeployment(unittest.TestCase):
    """Tests for Deployment resource class."""

    def setUp(self):
        config = client.APIConfig(url="http://localhost:8000/api/v1",
                                  token="token")
        deployments = endpoints.Deployments(config)
        self.raw_data = json.loads(load_fixture("ubuntu_deployment_data.json"))
        self.deployment = resources.Deployment(data=self.raw_data)
        self.deployment.register_update_endpoint(deployments)

    def test_attribute_proxying(self):
        self.assertFalse(self.deployment.archived)
        self.deployment.archived = True
        self.assertTrue(self.deployment.archived)
        self.assertTrue(self.deployment._data['archived'])
        self.assertTrue(self.deployment.asdict()['archived'])

    def test_asdict(self):
        """Test that asdict returns an exact matching directory."""
        # Make sure dictionaries are different instances
        self.assertIsNot(self.raw_data, self.deployment._data)
        self.assertEqual(self.raw_data, self.deployment.asdict())

    def test_child_task_mapping(self):
        """Test latest_task and launch_task mappings."""
        self.assertIsInstance(self.deployment.latest_task, resources.Task)
        self.assertIsInstance(self.deployment.launch_task, resources.Task)
        self.assertEqual(self.deployment.launch_task.id, 215)

    def test_update(self):
        """Test a no-op update and make sure it returns the same values."""
        self.deployment._update_endpoint.update = Mock(
            return_value=self.deployment)
        data = self.deployment.asdict()
        del data['id']
        self.deployment.update()
        self.deployment._update_endpoint.update.assert_called_with(
            self.deployment.id, **data)
        self.assertEqual(self.raw_data, self.deployment.asdict())

    def test_update_archived(self):
        """Test a update of archived field."""
        # Set up mocked response
        updated_data = copy.deepcopy(self.raw_data)
        updated_data['archived'] = True
        return_value = resources.Deployment(data=updated_data)
        return_value.register_update_endpoint(self.deployment._update_endpoint)
        self.deployment._update_endpoint.update = Mock(
            return_value=return_value)

        self.deployment.archived = True
        data = self.deployment.asdict()
        del data['id']
        self.assertTrue(data['archived'])
        self.deployment.update()
        # Verify mock called as expected
        self.deployment._update_endpoint.update.assert_called_with(
            self.deployment.id, **data)
        self.assertTrue(self.deployment.archived)
        self.assertEqual(updated_data, self.deployment.asdict())

    def test_public_ip(self):
        """Test public_ip computed property."""
        self.assertEqual(self.deployment.public_ip, "34.233.71.64")


class TestTask(unittest.TestCase):

    def setUp(self):
        config = client.APIConfig(url="http://localhost:8000/api/v1",
                                  token="token")
        deployments = endpoints.Deployments(config)
        self.deployment = resources.Deployment(data=json.loads(load_fixture("ubuntu_deployment_data.json")))
        # self.deployment = resources.Deployment(
        #     data=TestDeployment.DEPLOYMENT_DATA)
        self.deployment.register_update_endpoint(deployments)

    def test_instance_status(self):
        self.assertEqual(self.deployment.latest_task.instance_status,
                         "running")
        self.assertEqual(self.deployment.launch_task.instance_status,
                         None)


class TestApplication(unittest.TestCase):

    def setUp(self):
        config = client.APIConfig(url="http://localhost:8000/api/v1",
                                  token="token")
        applications = endpoints.Applications(config)
        self.application = resources.Application(
            data=json.loads(load_fixture("ubuntu_application_data.json")))
        self.application.register_update_endpoint(applications)

    def test_data_mapping(self):
        self.assertEqual(len(self.application.versions), 2)
        version1, version2 = self.application.versions
        self.assertTrue(isinstance(version1, resources.ApplicationVersion))
        self.assertTrue(isinstance(version2, resources.ApplicationVersion))
        self.assertEqual(len(version1.cloud_config), 2)
        for cloud_config in version1.cloud_config:
            self.assertTrue(
                isinstance(cloud_config,
                           resources.ApplicationVersionCloudConfig))
            self.assertTrue(isinstance(cloud_config.cloud, resources.Cloud))
            self.assertTrue(isinstance(cloud_config.image, resources.Image))
        self.assertEqual(len(version2.cloud_config), 4)
