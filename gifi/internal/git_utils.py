from gifi.command import CommandException
from git import Repo, InvalidGitRepositoryError


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
        try:
            repo = Repo('.')
        except InvalidGitRepositoryError:
            raise CommandException('To run this command you need to be in git source code directory.')
    return repo


def remote_origin_url(repo=None):
    repo = get_repo(repo)
    config_reader = repo.config_reader()
    origin_url = config_reader.get_value('remote "origin"', "url")
    config_reader.release()
    return origin_url


def get_from_last_commit_message(repo, item_header):
    commit_message_lines = repo.head.commit.message.split('\n')
    lines_with_item = [e for e in commit_message_lines if e.startswith(item_header)]
    items = map(lambda e: e.split('%s:' % item_header)[1].split(','), lines_with_item)
    items = [item.strip() for sub_list in items for item in sub_list]
    return items
