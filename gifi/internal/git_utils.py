from gifi.command import CommandException
from git import Repo


def current_branch(repo):
    current_branch = repo.git.rev_parse('--abbrev-ref', 'HEAD')
    return current_branch


def check_repo_is_clean(repo):
    if repo.is_dirty():
        raise CommandException('Please commit all untracked files.')


def get_repo(repo=None):
    """

    :rtype : git.Repo
    """
    if repo is None:
        repo = Repo('.')
    return repo
