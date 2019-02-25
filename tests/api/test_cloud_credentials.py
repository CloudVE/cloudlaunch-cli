import copy
import json
import os
import unittest

import tests

from cloudlaunch_cli.api import cloud_credentials

class TestGCECredentials(unittest.TestCase):

    def setUp(self):
        # Restore `os.environ` after each test
        self.original_environ = copy.deepcopy(os.environ)

    def tearDown(self):
        os.environ = self.original_environ

    def test_load_from_envvar_filepath(self):
        path = os.path.join(tests.fixtures_dir, "gcp_credentials.json")
        os.environ["GCP_CREDENTIALS_JSON"] = path
        self.assertEqual(os.getenv("GCP_CREDENTIALS_JSON"), path)

        gcp_credentials = cloud_credentials.GCPCredentials.from_environment()
        self.assertIsNotNone(gcp_credentials)
        http_headers = gcp_credentials.to_http_headers()
        self.assertTrue('cl-gcp-credentials-json' in http_headers)
        with open(path) as f:
            self.assertEqual(http_headers['cl-gcp-credentials-json'],
                             json.dumps(json.loads(f.read())))

    def test_load_from_envvar_string(self):
        path = os.path.join(tests.fixtures_dir, "gcp_credentials.json")
        with open(path) as f:
            os.environ["GCP_CREDENTIALS_JSON"] = json.dumps(json.loads(f.read()))

        gcp_credentials = cloud_credentials.GCPCredentials.from_environment()
        self.assertIsNotNone(gcp_credentials)
        http_headers = gcp_credentials.to_http_headers()
        self.assertTrue('cl-gcp-credentials-json' in http_headers)
        with open(path) as f:
            self.assertEqual(http_headers['cl-gcp-credentials-json'],
                             json.dumps(json.loads(f.read())))

    def test_load_from_dict(self):
        path = os.path.join(tests.fixtures_dir, "gcp_credentials.json")
        with open(path) as f:
            creds_dict = json.loads(f.read())

        gcp_credentials = cloud_credentials.GCPCredentials.from_dict(creds_dict)
        self.assertIsNotNone(gcp_credentials)
        http_headers = gcp_credentials.to_http_headers()
        self.assertTrue('cl-gcp-credentials-json' in http_headers)
        with open(path) as f:
            self.assertEqual(http_headers['cl-gcp-credentials-json'],
                             json.dumps(json.loads(f.read())))
