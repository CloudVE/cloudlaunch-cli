#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cloudlaunch_cli` package."""


import unittest

from click.testing import CliRunner

import cloudlaunch_cli.main


class TestCloudlaunch_cli(unittest.TestCase):
    """Tests for `cloudlaunch_cli` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cloudlaunch_cli.main.client)
        assert result.exit_code == 0
        assert 'Usage: client [OPTIONS] COMMAND [ARGS]' in result.output
        help_result = runner.invoke(cloudlaunch_cli.main.client, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
