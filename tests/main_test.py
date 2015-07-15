from difflib import unified_diff
from pprint import pprint
from tempfile import mkdtemp
from unittest import TestCase

from utils.git_test import AbstractGitReposTest
import os
from gifi.main import command, _main


def test_help():
    with open('tests/resources/expected_help.txt', 'r') as f:
        expected_help = f.readlines()
    actual_help = command('help')

    diff = list(unified_diff(expected_help, actual_help.splitlines(1)))
    pprint(diff)
    assert len(diff) == 0


def test_main_handles_unknown_command():
    _main(['wrong_command'])


def test_main_handles_no_command():
    _main([])


class AliasesInstallerTest(AbstractGitReposTest):
    def test_aliases_installer(self):
        command('install', 'repository')
        config_reader = self.local_repo.config_reader()
        config_reader.get_value('alias', 'queue-push')
        config_reader.get_value('alias', 'queue-list')
        config_reader.get_value('alias', 'queue-pop')
        config_reader.get_value('alias', 'feature-start')
        config_reader.get_value('alias', 'feature-finish')
        config_reader.get_value('alias', 'feature-publish')
        config_reader.get_value('alias', 'feature-configure')
        config_reader.release()

        # call one alias
        self.local_repo.git.__getattr__('queue-list')


class GifiWorksOutsideOfGit(TestCase):
    def setUp(self):
        self.old_working_dir = os.getcwd()
        os.chdir(mkdtemp())

    def tearDown(self):
        os.chdir(self.old_working_dir)

    def test_version(self):
        _main(['version'])

    def test_repo_dependant_command(self):
        # no unhandled exception is thrown
        _main(['feature', 'publish'])
