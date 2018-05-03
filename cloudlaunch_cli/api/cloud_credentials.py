"""Utilities for handling cloud credentials."""
import abc
import json
import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)


class CloudCredentials(abc.ABC):
    """Base class representing cloud credentials."""

    @staticmethod
    def load_from_environment(cloud_type):
        """Load a CloudCredentials subclass instance from env vars."""
        if cloud_type == 'aws':
            return AWSCredentials.from_environment()
        elif cloud_type == 'gce':
            return GCECredentials.from_environment()
        elif cloud_type == 'openstack':
            return OpenStackCredentials.from_environment()
        elif cloud_type == 'azure':
            return AzureCredentials.from_environment()
        return None

    @staticmethod
    def load_from_dict(cloud_type, creds_dict):
        """Load a CloudCredentials subclass instance from given dict."""
        if cloud_type == 'aws':
            return AWSCredentials.from_dict(creds_dict)
        elif cloud_type == 'gce':
            return GCECredentials.from_dict(creds_dict)
        elif cloud_type == 'openstack':
            return OpenStackCredentials.from_dict(creds_dict)
        elif cloud_type == 'azure':
            return AzureCredentials.from_dict(creds_dict)
        return None

    @staticmethod
    @abc.abstractmethod
    def from_environment():
        """Load and return an instance of CloudCredentials using env vars."""
        pass

    @staticmethod
    @abc.abstractmethod
    def from_dict(creds_dict):
        """Load and return an instance of CloudCredentials from given dict."""
        pass

    @abc.abstractmethod
    def to_http_headers(self):
        """Convert credentials to dict of http header name/values."""
        pass


class AWSCredentials(CloudCredentials):
    """CloudCredentials subclass representing AWS credentials."""

    def __init__(self, aws_access_key, aws_secret_key):
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key

    @staticmethod
    def from_environment():
        aws_access_key = os.environ.get('AWS_ACCESS_KEY')
        aws_secret_key = os.environ.get('AWS_SECRET_KEY')
        if aws_access_key and aws_secret_key:
            return AWSCredentials(aws_access_key, aws_secret_key)
        else:
            return None

    @staticmethod
    def from_dict(creds_dict):
        aws_access_key = creds_dict.get('aws_access_key')
        aws_secret_key = creds_dict.get('aws_secret_key')
        if aws_access_key and aws_secret_key:
            return AWSCredentials(aws_access_key, aws_secret_key)
        else:
            return None

    def to_http_headers(self):
        return {
            'cl-aws-access-key': self.aws_access_key,
            'cl-aws-secret-key': self.aws_secret_key
        }


class GCECredentials(CloudCredentials):
    """CloudCredentials subclass representing AWS credentials."""

    def __init__(self, creds_dict):
        self.creds_dict = creds_dict

    @staticmethod
    def from_environment():
        gce_credentials_json = os.environ.get('GCE_CREDENTIALS_JSON')

        creds_dict = None
        if gce_credentials_json:
            try:
                # Try to read as JSON string first, then try as a file path
                creds_dict = GCECredentials._safe_load_json(
                    gce_credentials_json)
                if not creds_dict:
                    gce_credentials_json_path = Path(gce_credentials_json)
                    if gce_credentials_json_path.exists():
                        with gce_credentials_json_path.open() as f:
                            creds_dict = json.loads(f.read())
            except Exception as e:
                log.error("Unable to read GCE_CREDENTIALS_JSON: " + str(e),
                          exc_info=e)
        if creds_dict:
            return GCECredentials(creds_dict)
        else:
            return None

    @staticmethod
    def from_dict(creds_dict):
        return GCECredentials(creds_dict)

    def to_http_headers(self):
        return {
            'cl-gce-credentials-json': json.dumps(self.creds_dict),
        }

    @staticmethod
    def _safe_load_json(value):
        try:
            return json.loads(value)
        except Exception as e:
            return None


class OpenStackCredentials(CloudCredentials):
    """CloudCredentials subclass representing OpenStack credentials."""

    def __init__(self, os_username, os_password, os_project_name=None,
                 os_project_domain_name=None, os_user_domain_name=None):
        self.os_username = os_username
        self.os_password = os_password
        self.os_project_name = os_project_name
        self.os_project_domain_name = os_project_domain_name
        self.os_user_domain_name = os_user_domain_name

    @staticmethod
    def from_environment():
        os_username = os.environ.get('OS_USERNAME')
        os_password = os.environ.get('OS_PASSWORD')
        if os_username and os_password:
            os_project_name = os.environ.get('OS_PROJECT_NAME')
            os_project_domain_name = os.environ.get('OS_PROJECT_DOMAIN_NAME')
            os_user_domain_name = os.environ.get('OS_USER_DOMAIN_NAME')
            return OpenStackCredentials(
                os_username, os_password,
                os_project_name=os_project_name,
                os_project_domain_name=os_project_domain_name,
                os_user_domain_name=os_user_domain_name)
        else:
            return None

    @staticmethod
    def from_dict(creds_dict):
        os_username = creds_dict.get('os_username')
        os_password = creds_dict.get('os_password')
        if os_username and os_password:
            os_project_name = creds_dict.get('os_project_name')
            os_project_domain_name = creds_dict.get('os_project_domain_name')
            os_user_domain_name = creds_dict.get('os_user_domain_name')
            return OpenStackCredentials(
                os_username, os_password,
                os_project_name=os_project_name,
                os_project_domain_name=os_project_domain_name,
                os_user_domain_name=os_user_domain_name)
        else:
            return None

    def to_http_headers(self):
        http_headers = {
            'cl-os-username': self.os_username,
            'cl-os-password': self.os_password,
        }
        if self.os_project_name:
            http_headers['cl-os-project-name'] = self.os_project_name
        if self.os_project_domain_name:
            http_headers['cl-os-project-domain-name'] =\
                self.os_project_domain_name
        if self.os_user_domain_name:
            http_headers['cl-os-user-domain-name'] = self.os_user_domain_name
        return http_headers


class AzureCredentials(CloudCredentials):
    """CloudCredentials subclass representing Azure credentials."""

    def __init__(self, azure_subscription_id, azure_client_id, azure_secret,
                 azure_tenant, azure_resource_group=None,
                 azure_storage_account=None, azure_vm_default_username=None):
        self.azure_subscription_id = azure_subscription_id
        self.azure_client_id = azure_client_id
        self.azure_secret = azure_secret
        self.azure_tenant = azure_tenant
        self.azure_resource_group = azure_resource_group
        self.azure_storage_account = azure_storage_account
        self.azure_vm_default_username = azure_vm_default_username

    @staticmethod
    def from_environment():
        azure_subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID')
        azure_client_id = os.environ.get('AZURE_CLIENT_ID')
        azure_secret = os.environ.get('AZURE_SECRET')
        azure_tenant = os.environ.get('AZURE_TENANT')
        if azure_subscription_id and azure_client_id and azure_secret\
                and azure_tenant:
            azure_resource_group = os.environ.get('AZURE_RESOURCE_GROUP')
            azure_storage_account = os.environ.get('AZURE_STORAGE_ACCOUNT')
            azure_vm_default_username = \
                os.environ.get('AZURE_VM_DEFAULT_USERNAME')
            return AzureCredentials(
                azure_subscription_id, azure_client_id,
                azure_secret, azure_tenant,
                azure_resource_group=azure_resource_group,
                azure_storage_account=azure_storage_account,
                azure_vm_default_username=azure_vm_default_username)
        else:
            return None

    @staticmethod
    def from_dict(creds_dict):
        azure_subscription_id = creds_dict.get('azure_subscription_id')
        azure_client_id = creds_dict.get('azure_client_id')
        azure_secret = creds_dict.get('azure_secret')
        azure_tenant = os.environ.get('azure_tenant')
        if azure_subscription_id and azure_client_id and azure_secret\
                and azure_tenant:
            azure_resource_group = os.environ.get('azure_resource_group')
            azure_storage_account = creds_dict.get('azure_storage_account')
            azure_vm_default_username = \
                creds_dict.get('azure_vm_default_username')
            return AzureCredentials(
                azure_subscription_id, azure_client_id,
                azure_secret, azure_tenant,
                azure_resource_group=azure_resource_group,
                azure_storage_account=azure_storage_account,
                azure_vm_default_username=azure_vm_default_username)
        else:
            return None

    def to_http_headers(self):
        http_headers = {
            'cl-azure-subscription-id': self.azure_subscription_id,
            'cl-azure-client-id': self.azure_client_id,
            'cl-azure-secret': self.azure_secret,
            'cl-azure-tenant': self.azure_tenant,
        }
        if self.azure_resource_group:
            http_headers['cl-azure-resource-group'] = self.azure_resource_group
        if self.azure_storage_account:
            http_headers['cl-azure-storage-account'] = \
                self.azure_storage_account
        if self.azure_vm_default_username:
            http_headers['cl-azure-vm-default-username'] = \
                self.azure_vm_default_username
        return http_headers
