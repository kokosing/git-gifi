from git import Repo

from command import Command, AggregatedCommand, CommandException

repo = Repo('.')


def _check_repo_is_clean():
    assert not repo.is_dirty()


def _current_branch():
    return repo.git.rev_parse('--abbrev-ref', 'HEAD')


def _pop():
    _check_repo_is_clean()
    raise CommandException("Not implemented yet")


def _push():
    _check_repo_is_clean()
    raise CommandException("Not implemented yet")


command = AggregatedCommand('queue', 'Stash based commit queue.', [
    Command('pop', 'Pops a commit from the queue.', _pop),
    Command('push', 'Pushes a commit on the queue.', _push)
])
