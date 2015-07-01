from difflib import unified_diff
from pprint import pprint

from gifi.main import command, _main


def test_help():
    expected_help = '''gifi <subcommand>\t-\tGit and github enhancements to git.
Usage:
\tgifi command [command arguments]

Commands:
queue <subcommand>\t-\tStash based commit queue. See below subcommands:
\tpush\t-\tPushes a commit on the queue.
\tlist\t-\tList commits in the queue.
\tpop\t-\tPops a commit from the queue.

feature <subcommand>\t-\tManages a feature branches. See below subcommands:
\tstart <feature name>\t-\tCreates a new feature branch.
\tfinish\t-\tCloses and pushes a feature to a master branch.
\tpublish\t-\tPublishes a feature branch to review.

help\t-\tdisplay this window.
'''
    actual_help = command('help')

    diff = list(unified_diff(expected_help.splitlines(1), actual_help.splitlines(1)))
    pprint(diff)
    assert len(diff) == 0


def test_main_handles_unknown_command():
    _main(['wrong_command'])


def test_main_handles_no_command():
    _main([])
