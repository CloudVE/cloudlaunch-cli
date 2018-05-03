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
        path = os.path.join(tests.fixtures_dir, "gce_credentials.json")
        os.environ["GCE_CREDENTIALS_JSON"] = path
        self.assertEqual(os.getenv("GCE_CREDENTIALS_JSON"), path)

        gce_credentials = cloud_credentials.GCECredentials.from_environment()
        self.assertIsNotNone(gce_credentials)
        http_headers = gce_credentials.to_http_headers()
        self.assertTrue('cl-gce-credentials-json' in http_headers)
        with open(path) as f:
            self.assertEqual(http_headers['cl-gce-credentials-json'],
                             json.dumps(json.loads(f.read())))

    def test_load_from_envvar_string(self):
        path = os.path.join(tests.fixtures_dir, "gce_credentials.json")
        with open(path) as f:
            os.environ["GCE_CREDENTIALS_JSON"] = json.dumps(json.loads(f.read()))

        gce_credentials = cloud_credentials.GCECredentials.from_environment()
        self.assertIsNotNone(gce_credentials)
        http_headers = gce_credentials.to_http_headers()
        self.assertTrue('cl-gce-credentials-json' in http_headers)
        with open(path) as f:
            self.assertEqual(http_headers['cl-gce-credentials-json'],
                             json.dumps(json.loads(f.read())))

    def test_load_from_dict(self):
        path = os.path.join(tests.fixtures_dir, "gce_credentials.json")
        with open(path) as f:
            creds_dict = json.loads(f.read())

        gce_credentials = cloud_credentials.GCECredentials.from_dict(creds_dict)
        self.assertIsNotNone(gce_credentials)
        http_headers = gce_credentials.to_http_headers()
        self.assertTrue('cl-gce-credentials-json' in http_headers)
        with open(path) as f:
            self.assertEqual(http_headers['cl-gce-credentials-json'],
                             json.dumps(json.loads(f.read())))
