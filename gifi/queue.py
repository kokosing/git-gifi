from git import Repo

from command import Command, AggregatedCommand

repo = Repo('.')


def _check_repo_is_clean():
    assert not repo.is_dirty()


def _current_branch():
    return repo.git.rev_parse('--abbrev-ref', 'HEAD')


_pop = Command('pop', 'Pops a commit from the queue.', lambda: {
    _check_repo_is_clean()

})

_push = Command('push', 'Pushes a commit on the queue.', lambda: {
    _check_repo_is_clean()

})

command = AggregatedCommand('queue', 'Stash based commit queue.', [_pop, _push])
