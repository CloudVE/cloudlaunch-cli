import configparser
import os
from os.path import expanduser
from urllib.parse import urlparse

SECTION = 'cloudlaunch-cli'
API_URL_ROOT = 'api/v1'


class Configuration(object):

    def __init__(self):
        self._filename = "~/.cloudlaunch"
        self._read_config()

    @property
    def url(self):
        """
        URL with the full path to the REST API root.

        This URL is of the form:
        "scheme://domain.name(:port)/path/to/{API_URL_ROOT}"
        """.format(API_URL_ROOT=API_URL_ROOT)
        return (os.environ.get('CLOUDLAUNCH_SERVER_URL') or
                self._get_config_value("url"))

    @url.setter
    def url(self, value):
        url_parsed = urlparse(value)
        scheme = url_parsed.scheme
        netloc = url_parsed.netloc
        path = url_parsed.path
        if not scheme or not netloc or not path \
                or API_URL_ROOT not in path:
            raise Exception("URL is not in the required format: "
                            "scheme://domain.name(:port)/path/to/"
                            + API_URL_ROOT)
        # Strip off any part of the path after the API URL root
        updated_path = path[0:path.find(API_URL_ROOT)] + API_URL_ROOT
        self._set_config_value("url", "{scheme}://{netloc}{path}".format(
            scheme=scheme, netloc=netloc, path=updated_path))

    @property
    def token(self):
        return (os.environ.get('CLOUDLAUNCH_AUTH_TOKEN') or
                self._get_config_value("token"))

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
        return self._config[SECTION].get(name) \
            if SECTION in self._config else None

    def _set_config_value(self, name, value):
        if SECTION not in self._config:
            self._config[SECTION] = {}
        self._config[SECTION][name] = value
        self._write_config()

    def _get_config_values(self):
        return self._config[SECTION] if SECTION in self._config else {}
