from difflib import unified_diff

from pprint import pprint
import subprocess
from tempfile import mkdtemp
from unittest import TestCase

from gifi.main import command, _main
from internal.git_test import AbstractGitReposTest
import os


def test_help():
    expected_help = '''gifi <subcommand>\t-\tGit and github enhancements to git.
Usage:
\tgifi command [command arguments]

Commands:
github <subcommand>\t-\tIntegration with github. See below subcommands:
\tauthenticate\t-\tAuthenticate and retrieve github access token.
\trequest\t-\tCreates a pull request from current branch.
\tconfigure <configuration level>\t-\tConfigure github settings.

help\t-\tDisplay this window.
feature <subcommand>\t-\tManages a feature branches. See below subcommands:
\tstart <feature name>\t-\tCreates a new feature branch.
\tfinish\t-\tCloses and pushes a feature to a master branch.
\tconfigure <configuration level>\t-\tConfigure feature behaviour.
\tpublish\t-\tPublishes a feature branch to review.

queue <subcommand>\t-\tStash based commit queue. See below subcommands:
\tpush\t-\tPushes a commit on the queue.
\tpop-finish\t-\tIn case of conflict during 'pop', use this command once conflict is solved.
\tlist\t-\tList commits in the queue.
\tpop\t-\tPops a commit from the queue.

version\t-\tShow version number.
install\t-\tInstall gifi as git bunch of aliases.
slack <subcommand>\t-\tIntegration with slack. See below subcommands:
\tnotify <message>\t-\tPost a message on given channel.
\tconfigure <configuration level>\t-\tConfigure slack settings.

'''
    actual_help = command('help')

    diff = list(unified_diff(expected_help.splitlines(1), actual_help.splitlines(1)))
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
