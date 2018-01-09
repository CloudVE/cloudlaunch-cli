#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'coreapi == 2.2.3',
    'arrow==0.12.0',
]

setup_requirements = [
]

test_requirements = [
]

setup(
    name='cloudlaunch_cli',
    version='0.1.0',
    description="Command line client to the CloudLaunch API.",
    long_description=readme + '\n\n' + history,
    author="Galaxy and GVL Projects",
    author_email='help@CloudVE.org',
    url='https://github.com/CloudVE/cloudlaunch_cli',
    packages=find_packages(include=['cloudlaunch_cli']),
    entry_points={
        'console_scripts': [
            'cloudlaunch=cloudlaunch_cli.main:client'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='cloudlaunch_cli',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
