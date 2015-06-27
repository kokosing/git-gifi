from gifi.main import command, _main


def test_help():
    assert command('help') == '''gifi\t-\tGit and github enhancements to git.
Usage:
\tgifi command [command arguments]

Commands:
help\t-\tdisplay this window'''


def test_main_handles_unknown_command():
    _main(['wrong_command'])


def test_main_handles_no_command():
    _main([])
