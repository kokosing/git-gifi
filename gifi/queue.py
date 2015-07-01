from git import Repo
from internal import git_utils

from command import Command, AggregatedCommand


def _pop():
    repo = Repo('.')
    git_utils.check_repo_is_clean(repo)
    repo.git.stash('apply', '--index')
    commit_message = repo.git.stash('list', '--max-count=1', '--oneline')
    repo.index.commit(_unescape_new_lines(commit_message))
    repo.git.stash('drop')


def _push():
    repo = Repo('.')
    git_utils.check_repo_is_clean(repo)
    commit_message = repo.head.commit.message
    repo.git.reset('--soft', 'HEAD^')
    repo.git.stash('save', _escape_new_lines(commit_message))


def _list():
    repo = Repo('.')
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
    Command('push', 'Pushes a commit on the queue.', _push),
    Command('list', 'List commits in the queue.', _list)
])
