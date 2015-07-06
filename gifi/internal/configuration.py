from gifi.command import CommandException

_CONFIGURATION_PREFIX = 'gifi'


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
        return self._parse_value(rawValue, type(default))

    def _default(self, item):
        default = self.configuration[item][0]
        return default

    def list(self):
        return self.configuration.keys()

    def description(self, item):
        return self.configuration[item][1]

    def set(self, item, value):
        config_writer = self.repo.config_writer()
        config_writer.set_value(_CONFIGURATION_PREFIX, self._key(item), value)
        config_writer.release()

    def _key(self, item):
        return '%s-%s' % (self.prefix, item)

    def _parse_value(self, rawValue, destType):
        rawValue = str(rawValue)
        if destType is bool:
            if rawValue in ['True', 'true', 'yes', '1']:
                return True
            elif rawValue in ['False', 'false', 'no', '0']:
                return False
            else:
                raise CommandException("Wrong value '%s' (with: %s) for '%s'" % (rawValue, type(rawValue), destType))
        elif destType is str:
            return rawValue
        else:
            raise CommandException('Unsupported type: %s' % destType)

    def configure(self, keys=None):
        if keys is None:
            keys = self.list()
        for key in keys:
            current_value = self[key]
            new_value = raw_input("%s (%s): " % (self.description(key), current_value))
            if new_value is not '':
                self.set(key, self._parse_value(new_value, type(current_value)))
