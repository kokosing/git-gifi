from command import AggregatedCommand, Command, CommandException
from utils.configuration import Configuration
from utils.git_utils import get_repo
from ui import ask


def _print_list(repo=None):
    repo = get_repo(repo)
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
    pass

def _rm():
    pass

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
    Command('add', 'Add new epic branch.', _add, '<remote/branch>')
])
