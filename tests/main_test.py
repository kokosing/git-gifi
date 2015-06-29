from gifi.main import command, _main


def test_help():
    assert command('help') == '''gifi <subcommand>\t-\tGit and github enhancements to git.
Usage:
\tgifi command [command arguments]

Commands:
feature <subcommand>\t-\tManages a feature branches. See below subcommands:
\tstart <feature name>\t-\tCreates a new feature branch.
\tfinish\t-\tCloses and pushes a feature to a master branch.

help\t-\tdisplay this window.
'''

def test_main_handles_unknown_command():
    _main(['wrong_command'])


def test_main_handles_no_command():
    _main([])
