import configparser
from os.path import expanduser

def get_config_value(name):
    config = configparser.ConfigParser()
    config.read(expanduser("~/.cloudlaunch"))
    return config['cloudlaunch-cli'].get(name, None) if 'cloudlaunch-cli' in config else None

def set_config_value(name, value):
    # TODO: make sure that 'url' is of the right format
    config = configparser.ConfigParser()
    config.read(expanduser("~/.cloudlaunch"))
    if 'cloudlaunch-cli' not in config:
        config['cloudlaunch-cli'] = {}
    config['cloudlaunch-cli'][name] = value
    with open(expanduser("~/.cloudlaunch"), 'w') as configfile:
        config.write(configfile)

def get_config_values():
    config = configparser.ConfigParser()
    config.read(expanduser("~/.cloudlaunch"))
    return config['cloudlaunch-cli'] if 'cloudlaunch-cli' in config else {}
