from tests.utils.git_test import AbstractGitReposTest
from gifi.utils.git_utils import get_from_last_commit_message


class GitUtilsTest(AbstractGitReposTest):
    def test_one_value_tag(self):
        self.commit_local_file('tmp', 'tag: one')
        assert get_from_last_commit_message(self.local_repo, 'tag') == ['one']

    def test_multiple_values_tag(self):
        self.commit_local_file('tmp', 'tag: one, two, three')
        assert get_from_last_commit_message(self.local_repo, 'tag') == ['one', 'two', 'three']
