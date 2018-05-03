# -*- coding: utf-8 -*-

"""Unit test package for cloudlaunch_cli."""

import os

fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')


def load_fixture(filename):
    with open(os.path.join(fixtures_dir, filename)) as f:
        return f.read()
