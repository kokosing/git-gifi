from command import Command, AggregatedCommand, CommandException
from internal.git_utils import get_repo, check_repo_is_clean


def _pop():
    repo = get_repo()
    check_repo_is_clean(repo)
    if repo.git.stash('list') == '':
        raise CommandException('There is nothing in the queue to pop from.')
    repo.git.stash('apply', '--index')
    _pop_finish()


def _pop_finish(repo=None):
    repo = get_repo(repo)
    commit_message = repo.git.stash('list', '--max-count=1', '--oneline')
    commit_message = ': '.join(commit_message.split(': ')[2:])
    repo.index.commit(_unescape_new_lines(commit_message))
    repo.git.stash('drop')


def _push():
    repo = get_repo()
    check_repo_is_clean(repo)
    if repo.head.commit == repo.commit('origin/master'):
        raise CommandException('You are currently at origin/master, there is nothing to push')
    commit_message = repo.head.commit.message
    repo.git.reset('--soft', 'HEAD^')
    repo.git.stash('save', _escape_new_lines(commit_message))


def _list():
    repo = get_repo()
    return repo.git.stash('list')


def _escape_new_lines(commit_message):
    """

    :type commit_message: str
    """
    return commit_message.replace('\n', '$$')


def _unescape_new_lines(commit_message):
    """

    :type commit_message: str
    """
    return commit_message.replace('$$', '\n')


command = AggregatedCommand('queue', 'Stash based commit queue.', [
    Command('pop', 'Pops a commit from the queue.', _pop),
    Command('pop-finish', "In case of conflict during 'pop', use this command once conflict is solved.", _pop_finish),
    Command('push', 'Pushes a commit on the queue.', _push),
    Command('list', 'List commits in the queue.', _list)
])
