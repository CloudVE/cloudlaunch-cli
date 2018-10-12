===============
CloudLaunch CLI
===============

.. image:: https://travis-ci.org/CloudVE/cloudlaunch-cli.svg?branch=master
        :target: https://travis-ci.org/CloudVE/cloudlaunch-cli

.. image:: https://coveralls.io/repos/github/CloudVE/cloudlaunch-cli/badge.svg?branch=master
        :target: https://coveralls.io/github/CloudVE/cloudlaunch-cli?branch=master

.. image:: https://img.shields.io/pypi/v/cloudlaunch_cli.svg
        :target: https://pypi.python.org/pypi/cloudlaunch_cli

.. image:: https://readthedocs.org/projects/cloudlaunch-cli/badge/?version=latest
        :target: https://cloudlaunch-cli.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/CloudVE/cloudlaunch_cli/shield.svg
     :target: https://pyup.io/repos/github/CloudVE/cloudlaunch_cli/
     :alt: Updates


Command line client to the CloudLaunch API.


* Free software: MIT license
* Documentation: https://cloudlaunch-cli.readthedocs.io.


Quickstart
==========

1. Create a virtual environment and activate it
   ::

       python3 -m venv venv
       source venv/bin/activate

2. Install ``cloudlaunch-cli`` with pip
   ::

       pip install cloudlaunch-cli

3. The CloudLaunch CLI requires two config settings. First is the URL of
   the API root:
   ::

       cloudlaunch config set url https://launch.usegalaxy.org/cloudlaunch/api/v1

4. Second config setting is an auth token. To get an auth token, first
   log into CloudLaunch, for example, by going to
   https://launch.usegalaxy.org/login. Then navigate to the
   ``/api/v1/auth/tokens`` API endpoint, for example,
   https://launch.usegalaxy.org/cloudlaunch/api/v1/auth/tokens/.
   Copy the token out of the JSON response and then run the following
   (substituting your own token instead):
   ::

       cloudlaunch config set token b38faadf2ef6d59ce46711ed73e99d6...

5. Now you should be able to list your deployments
   ::

       cloudlaunch deployments list

6. You can create a deployment as well
   ::

       cloudlaunch deployments create my-ubuntu-test ubuntu \
           amazon-us-east-n-virginia --application-version 16.04

Installing for development
==========================

1. ``python3 -m venv venv``
2. ``source venv/bin/activate``
3. ``pip install -r requirements_dev.txt``

Now you can run ``cloudlaunch``.

Release process
===============

::

    bumpversion patch
    # or `bumpversion minor` or `bumpversion major`
    git push
    git push --tags
    make release

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
