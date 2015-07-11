from tests.utils.git_test import AbstractGitReposTest
import mock
from gifi.command import CommandException
from gifi.utils.configuration import Configuration, configuration_command


class ConfigurationTest(AbstractGitReposTest):
    def test_happy_path(self):
        config = self._create_test_config()

        assert config.sample == 'sample_default_value'
        assert config['sample'] == 'sample_default_value'
        assert config.list() == ['sample']
        assert config.description('sample') == 'Sample description'

        config.set('sample', 'new value')
        assert config.sample == 'new value'

        newConfig = self._create_test_config()
        assert newConfig.sample == 'new value'

    def _create_test_config(self):
        config = Configuration(self.local_repo, 'test', {
            'sample': ('sample_default_value', 'Sample description')
        })
        return config

    def test_configure(self):
        config = self._bool_config()

        with mock.patch('__builtin__.raw_input', return_value='true'):
            config.configure()
        assert config.bool_property == True

    def test_configure_with_wrong_input(self):
        config = self._bool_config()

        with mock.patch('__builtin__.raw_input', return_value='wrong value'):
            expected_msg = ".*Wrong value.*"
            with self.assertRaisesRegexp(CommandException, expected_msg):
                config.configure()

        assert config.bool_property == False

    def _bool_config(self):
        config = Configuration(self.local_repo, 'test', {
            'bool-property': (False, 'Description')
        })
        return config

    def test_configure_with_no_input(self):
        config = self._create_test_config()
        with mock.patch('__builtin__.raw_input', return_value=''):
            config.configure()

        assert config.sample == 'sample_default_value'

    def test_command(self):
        with mock.patch('__builtin__.raw_input', return_value=''):
            configuration_command(self._create_test_config, "description")()
