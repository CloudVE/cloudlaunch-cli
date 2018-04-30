"""Utilities for handling cloud credentials."""
import abc
import os


class CloudCredentials(abc.ABC):
    """Base class representing cloud credentials."""

    @staticmethod
    def load_from_environment(cloud_type):
        """Load a CloudCredentials subclass instance from env vars."""
        if cloud_type == 'aws':
            return AWSCredentials.from_environment()
        return None

    @staticmethod
    @abc.abstractmethod
    def from_environment():
        """Load and return an instance of CloudCredentials using env vars."""
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

    def to_http_headers(self):
        return {
            'cl-aws-access-key': self.aws_access_key,
            'cl-aws-secret-key': self.aws_secret_key
        }
