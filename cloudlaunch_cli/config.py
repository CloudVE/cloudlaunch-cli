import configparser
from os.path import expanduser
from urllib.parse import urlparse

SECTION = 'cloudlaunch-cli'


class Configuration(object):

    def __init__(self):
        self._filename = "~/.cloudlaunch"
        self._read_config()

    @property
    def url(self):
        return self._get_config_value("url")

    @url.setter
    def url(self, value):
        url_parsed = urlparse(value)
        if not url_parsed.scheme or not url_parsed.netloc:
            raise Exception("URL is not in the required format: scheme://domain.name(:port)")
        self._set_config_value("url", "{scheme}://{netloc}".format(**url_parsed._asdict()))

    @property
    def token(self):
        return self._get_config_value("token")

    @token.setter
    def token(self, value):
        self._set_config_value("token", value)

    def asdict(self):
        return self._config[SECTION]

    def _read_config(self):
        self._config = configparser.ConfigParser()
        self._config.read(expanduser(self._filename))

    def _write_config(self):
        with open(expanduser(self._filename), 'w') as configfile:
            self._config.write(configfile)

    def _get_config_value(self, name):
        return self._config[SECTION].get(name, None) if SECTION in self._config else None

    def _set_config_value(self, name, value):
        if SECTION not in self._config:
            self._config[SECTION] = {}
        self._config[SECTION][name] = value
        self._write_config()

    def _get_config_values(self):
        return self._config[SECTION] if SECTION in self._config else {}
