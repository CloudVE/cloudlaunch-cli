from setuptools import setup

setup(
    name='cloudlaunch-cli',
    version='0.1',
    packages=['cloudlaunch_cli'],
    install_requires=[
        'Click',
        'coreapi == 2.2.3',
        'arrow==0.12.0',
    ],
    entry_points='''
        [console_scripts]
        cloudlaunch=cloudlaunch_cli.main:client
    ''',
)
