from gifi.command import CommandException
from gifi.queue import command as queue
from tests.utils.git_test import AbstractGitReposTest


class QueueTest(AbstractGitReposTest):
    def test_happy_path(self):
        assert queue('list') == ''
        assert self.local_files_count() == 2

        with self.assertRaisesRegexp(CommandException, '.*nothing to push.*'):
            queue('push')

        self.commit_local_file('test_file')
        assert self.local_files_count() == 3

        queue('push')
        assert self.local_files_count() == 2
        list = queue('list')
        assert 'Add' in list and 'test_file' in list

        queue('pop')
        assert self.local_files_count() == 3
        assert queue('list') == ''

        with self.assertRaisesRegexp(CommandException, '.*nothing.*to pop from.*'):
            queue('pop')
