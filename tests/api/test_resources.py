
import copy
import unittest
from unittest.mock import Mock

from cloudlaunch_cli.api import client, endpoints, resources


class TestDeployment(unittest.TestCase):
    """Tests for Deployment resource class."""

    DEPLOYMENT_DATA = {
        "id": 26,
        "name": "my-ubuntu-test",
        "application_version": 5,
        "target_cloud": "amazon-us-east-n-virginia",
        "provider_settings": None,
        "application_config": {
            "config_cloudlaunch": {
                "instanceType": "t2.small",
                "firewall": [
                    {
                        "securityGroup": "cloudlaunch-vm",
                        "rules": [
                            {
                                "protocol": "tcp",
                                "from": "80",
                                "to": "80",
                                "cidr": "0.0.0.0/0"
                            },
                            {
                                "protocol": "tcp",
                                "from": "22",
                                "to": "22",
                                "cidr": "0.0.0.0/0"
                            }
                        ]
                    }
                ],
                "vmType": "t1.micro"
            }
        },
        "added": "2018-03-28T13:09:50.626923-04:00",
        "updated": "2018-03-28T13:21:15.746148-04:00",
        "owner": "machristie",
        "app_version_details": {
            "version": "16.04",
            "frontend_component_path":
                "app/marketplace/plugins/plugins.module#PluginsModule",
            "frontend_component_name": "ubuntu-config",
            "application": {
                "slug": "ubuntu",
                "name": "Ubuntu"
            }
        },
        "tasks": "http://127.0.0.1:4200/api/v1/deployments/26/tasks/",
        "latest_task": {
            "id": 216,
            "url": "http://127.0.0.1:4200/api/v1/deployments/26/tasks/216/",
            "celery_id": None,
            "action": "HEALTH_CHECK",
            "status": "SUCCESS",
            "result": {
                "instance_status": "running"
            },
            "traceback": None,
            "added": "2018-03-28T13:16:58.675260-04:00",
            "updated": "2018-03-28T13:17:01.329800-04:00",
            "deployment": 26
        },
        "launch_task": {
            "id": 215,
            "url": "http://127.0.0.1:4200/api/v1/deployments/26/tasks/215/",
            "celery_id": None,
            "action": "LAUNCH",
            "status": "SUCCESS",
            "result": {
                "cloudLaunch": {
                    "keyPair": {
                        "id": "cloudlaunch_key_pair",
                        "name": "cloudlaunch_key_pair",
                        "material": None
                    },
                    "securityGroup": {
                        "id": "sg-ec40da9e",
                        "name": "cloudlaunch-vm"
                    },
                    "instance": {
                        "id": "i-043d1b4d61e9065b8"
                    },
                    "publicIP": "34.233.71.64"
                }
            },
            "traceback": None,
            "added": "2018-03-28T13:09:50.638217-04:00",
            "updated": "2018-03-28T14:10:15.831364-04:00",
            "deployment": 26
        },
        "archived": False,
        "credentials": 2
    }

    def setUp(self):
        config = client.APIConfig(url="http://localhost:8000/api/v1",
                                  token="token")
        deployments = endpoints.Deployments(config)
        self.deployment = resources.Deployment(data=self.DEPLOYMENT_DATA)
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
        self.assertIsNot(self.DEPLOYMENT_DATA, self.deployment._data)
        self.assertEqual(self.DEPLOYMENT_DATA, self.deployment.asdict())

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
        self.assertEqual(self.DEPLOYMENT_DATA, self.deployment.asdict())

    def test_update_archived(self):
        """Test a update of archived field."""
        # Set up mocked response
        updated_data = copy.deepcopy(self.DEPLOYMENT_DATA)
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


class TestTask(TestDeployment):

    def test_instance_status(self):
        self.assertEqual(self.deployment.latest_task.instance_status,
                         "running")
        self.assertEqual(self.deployment.launch_task.instance_status,
                         None)
