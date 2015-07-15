from gifi.feature import command as feature
from gifi.utils.git_utils import get_current_branch
from tests.utils.git_test import AbstractGitReposTest


class FutureTest(AbstractGitReposTest):
    def test_happy_path(self):
        assert self.local_files_count() == 2
        assert self.local_heads_count() == 1
        assert self.remote_files_count() == 2
        assert self.remote_heads_count() == 1

        feature('start', 'test')
        assert self.local_files_count() == 2
        assert self.local_heads_count() == 2
        assert self.remote_files_count() == 2
        assert self.remote_heads_count() == 1
        assert get_current_branch(self.local_repo) == 'feature_test'

        self.commit_local_file('feature_test_file')
        feature('publish')
        assert self.local_files_count() == 3
        assert self.local_heads_count() == 2
        assert self.remote_files_count() == 2
        assert self.remote_heads_count() == 2
        assert self.remote_files_count('feature_test') == 3

        feature('finish')
        assert self.local_files_count() == 3
        assert self.local_heads_count() == 1
        assert self.remote_files_count() == 3
        assert self.remote_heads_count() == 1
