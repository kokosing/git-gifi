from command import AggregatedCommand, Command, CommandException
from utils.configuration import Configuration
from utils.git_utils import get_repo
from utils.ui import ask


def _print_list(repo=None, config=None):
    repo = get_repo(repo)
    if config is None:
        config = configuration(repo)

    print 'List of epics:'
    i = 0
    for epic in _list_all(config):
        i = i + 1
        print '%d - %s' % (i, epic)


def _list_all(config):
    return config.all.split(',')


def _add(epic):
    if epic is None:
        raise CommandException('No epic remote/branch given')
    repo = get_repo()
    config = configuration(repo)
    if epic in _list_all(config):
        raise CommandException('Epic %s is already added to the list' % epic)
    config.set('all', '%s,%s' % (config.all, epic))


def _select():
    repo = get_repo()
    config = configuration(repo)
    _print_list(repo, config)
    answer = ask('Which epic would you like to select', 1)
    config.set('current', _list_all(config)[answer - 1])


def _rm():
    repo = get_repo()
    config = configuration(repo)
    _print_list(repo, config)
    answer = ask('Which epic would you like to remove', 1)
    epics = _list_all(config)
    del epics[answer - 1]
    config.set('all', ','.join(epics))


def _current():
    repo = get_repo()
    config = configuration(repo)
    print config.current


def configuration(repo=None):
    repo = get_repo(repo)
    return Configuration(repo, 'epic', {
        'all': ('origin/master', 'A list of coma separated epic remote/branch`es'),
        'current': ('origin/master', 'Current epci remote/branch')
    })


command = AggregatedCommand('epic', 'Manages a epic branches.', [
    Command('list', 'List all epic branches.', _print_list),
    Command('select', 'Select your current epic branch.', _select),
    Command('rm', 'Remove epic branch.', _rm),
    Command('current', 'Print current epic branch.', _current),
    Command('add', 'Add new epic branch.', _add, '<remote/branch>')
])
