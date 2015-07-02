from tests.internal.git_test import AbstractGitReposTest
from gifi.internal.configuration import Configuration

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
