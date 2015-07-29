from tests.utils.git_test import AbstractGitReposTest
from gifi.utils.git_utils import get_from_last_commit_message


class GitUtilsTest(AbstractGitReposTest):
    def test_one_value_tag(self):
        self.commit_local_file('tmp', 'tag: one')
        self.assertEqual(get_from_last_commit_message(self.local_repo, 'tag'), ['one'])

    def test_case_insensitive_tag(self):
        self.commit_local_file('tmp', 'tAg: one')
        self.assertEqual(get_from_last_commit_message(self.local_repo, 'TaG'), ['one'])

    def test_multiple_values_tag(self):
        self.commit_local_file('tmp', 'tag: one, two, three')
        self.assertEqual(get_from_last_commit_message(self.local_repo, 'tag'), ['one', 'two', 'three'])

    def test_tag_no_colon(self):
        self.commit_local_file('tmp', 'tag one')
        self.assertEqual(get_from_last_commit_message(self.local_repo, 'tag'), [])

    def test_no_tag_value(self):
        self.commit_local_file('tmp', 'tmp')
        self.assertEqual(get_from_last_commit_message(self.local_repo, 'tag'), [])
