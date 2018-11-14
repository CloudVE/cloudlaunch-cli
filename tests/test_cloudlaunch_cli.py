#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cloudlaunch_cli` package."""
import os
import unittest

from click.testing import CliRunner

import cloudlaunch_cli.main


class TestCloudlaunch_cli(unittest.TestCase):
    """Tests for `cloudlaunch_cli` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def _get_test_resource(self, filename):
        return os.path.join(self._get_test_resource_path(), filename)

    def _get_test_resource_path(self):
        return os.path.join(os.path.dirname(__file__), 'fixtures/')

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cloudlaunch_cli.main.client)
        self.assertEqual(
            result.exit_code, 0,
            msg="invoking cli failed: " + str(result.exception))
        assert 'Usage: client [OPTIONS] COMMAND [ARGS]' in result.output
        help_result = runner.invoke(cloudlaunch_cli.main.client, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output

    def test_list_applications(self):
        """Test listing applications via CLI"""
        runner = CliRunner()
        result = runner.invoke(cloudlaunch_cli.main.client,
                               args=["applications", "list"])
        self.assertEqual(
            result.exit_code, 0,
            msg="listing apps failed: " + str(result.exception))
        # Verify result columns are in list output
        assert 'Genomics Virtual Lab' in result.output
        assert 'CloudLaunch integration' in result.output
        assert 'cloudve.org' in result.output
        assert 'An app that uses mock drivers' in result.output

    def test_create_deployments(self):
        """Test creating a deployment via the CLI"""
        runner = CliRunner()
        result = runner.invoke(
            cloudlaunch_cli.main.client,
            args=["deployments", "create", "cli-test-app", "cl_test_app",
                  "amazon-us-east-n-virginia",
                  "--application-version", "16.04",
                  "--config-app",
                  self._get_test_resource("app_cfg_ubuntu.json")])
        self.assertEqual(
            result.exit_code, 0,
            msg="create deployment failed: " + str(result.exception))
        assert('cli-test-app' in result.output)
