#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.rst') as changelog_file:
    changelog = changelog_file.read()

REQS_BASE = [
    'Click>=6.0',
    'coreapi==2.2.3',
    'arrow==0.12.0',
]

REQS_TEST = ([
    'tox>=2.9.1',
    'coverage>=4.4.1',
    'flake8>=3.4.1',
    'flake8-import-order>=0.13'] + REQS_BASE
)

REQS_DEV = ([
    'sphinx>=1.3.1',
    'bumpversion>=0.5.3',
    'twine'] + REQS_TEST
)

setup_requirements = [
    'wheel'
]

setup(
    name='cloudlaunch_cli',
    version='0.2.0',
    description="Command line client to the CloudLaunch API.",
    long_description=readme + '\n\n' + changelog,
    author="Galaxy and GVL Projects",
    author_email='help@CloudVE.org',
    url='https://github.com/CloudVE/cloudlaunch_cli',
    packages=find_packages(include=['cloudlaunch_cli', 'cloudlaunch_cli.*']),
    entry_points={
        'console_scripts': [
            'cloudlaunch=cloudlaunch_cli.main:client'
        ]
    },
    include_package_data=True,
    install_requires=REQS_BASE,
    extras_require={
        'dev': REQS_DEV,
        'test': REQS_TEST
    },
    license="MIT license",
    zip_safe=False,
    keywords='cloudlaunch_cli',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=REQS_TEST,
    setup_requires=setup_requirements,
)
