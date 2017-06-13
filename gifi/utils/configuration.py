from gifi.command import Command
from gifi.utils.ui import ask, parse_value

_CONFIGURATION_PREFIX = 'gifi'

NOT_SET = 'not-set'

REPOSITORY_CONFIG_LEVEL = 'repository'
GLOBAL_CONFIG_LEVEL = 'global'


class Configuration(object):
    def __init__(self, repo, prefix, configuration):
        """

        :type repo: git.Repo
        """
        self.repo = repo
        self.prefix = prefix
        self.configuration = configuration

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __getitem__(self, item):
        item = item.replace('_', '-')
        config_reader = self.repo.config_reader()
        default = self._default(item)
        rawValue = config_reader.get_value(_CONFIGURATION_PREFIX, self._key(item), default)
        config_reader.release()
        return parse_value(rawValue, type(default))

    def _default(self, item):
        return self.configuration[item][0]

    def list(self):
        return self.configuration.keys()

    def description(self, item):
        return self.configuration[item][1]

    def set(self, item, value, config_level=REPOSITORY_CONFIG_LEVEL):
        config_writer = self.repo.config_writer(config_level)
        config_writer.set_value(_CONFIGURATION_PREFIX, self._key(item), value)
        config_writer.release()

    def _key(self, item):
        return '%s-%s' % (self.prefix, item)

    def configure(self, config_level=REPOSITORY_CONFIG_LEVEL, keys=None):
        if keys is None:
            keys = self.list()
        for key in keys:
            value = self[key]
            value = ask("%s - %s" % (key, self.description(key)), value)
            self.set(key, value, config_level)


def configuration_command(configuration, description):
    return Command(
        'configure',
        description,
        lambda config_level=REPOSITORY_CONFIG_LEVEL: configuration().configure(config_level),
        '<configuration level>')
