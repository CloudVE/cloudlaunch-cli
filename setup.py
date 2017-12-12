from setuptools import setup

setup(
    name='cloudlaunch-cli',
    version='0.1',
    py_modules=['main'],
    install_requires=[
        'Click',
        'coreapi == 2.2.3',
    ],
    entry_points='''
        [console_scripts]
        cloudlaunch=main:client
    ''',
)