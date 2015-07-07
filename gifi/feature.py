from git import Repo

from internal import git_utils
from internal.configuration import Configuration

from command import AggregatedCommand, Command, CommandException
from internal.git_utils import get_repo, check_repo_is_clean, remote_origin_url
from git_hub import get_github

_FEATURE_BRANCH_PREFIX = 'feature_'


def _start(feature):
    repo = Repo('.')
    if feature is None:
        raise CommandException('No feature name given')

    feature_branch = '%s%s' % (_FEATURE_BRANCH_PREFIX, feature)
    git_utils.check_repo_is_clean(repo)

    if map(lambda head: head.name, repo.heads).count(feature_branch) != 0:
        raise CommandException("Feature branch '%s' already exists." % feature_branch)

    repo.git.fetch()
    repo.create_head(feature_branch, 'origin/master')
    repo.heads[feature_branch].checkout()


def _publish():
    repo = get_repo()
    check_repo_is_clean(repo)
    current_branch = _current_feature_branch(repo)
    repo.git.push('-f', '-u', 'origin', 'HEAD:%s' % current_branch)
    config = _configuration(repo)
    if config.publish_with_pull_request:
        origin_url = remote_origin_url(repo)
        full_repo_name = origin_url.split(':')[1].split('.')[0]

        pull = get_github(repo).get_repo(full_repo_name).create_pull(
            title=repo.head.commit.summary,
            body=repo.head.commit.message,
            head=current_branch,
            base='master'
        )
        repo.git.commit('--amend', '-m', '%s\n\nPull request: %s' % (repo.head.commit.message, pull.html_url))
        return 'Pull request URL: %s' % pull.html_url


def _finish():
    repo = get_repo()
    check_repo_is_clean(repo)
    config = _configuration(repo)
    current_branch = _current_feature_branch(repo)
    repo.git.fetch()
    if config.finish_with_rebase_interactive:
        repo.git.rebase('origin/master', '-i')
    else:
        repo.git.rebase('origin/master')
    repo.git.push('-f', 'origin', 'HEAD:%s' % current_branch)
    repo.git.push('origin', 'HEAD:master')
    repo.git.checkout('master')
    repo.git.rebase('origin/master')
    repo.git.push('origin', ':%s' % current_branch)
    repo.git.branch('-D', current_branch)


def _configure():
    _configuration().configure()


def _configuration(repo=None):
    repo = get_repo(repo)
    return Configuration(repo, 'feature', {
        'finish-with-rebase-interactive': (False, 'Should do a rebase interactive during feature finishing'),
        'publish-with-pull-request': (False, 'Should create a pull request during feature publishing')
    })


def _current_feature_branch(repo):
    current_branch = git_utils.current_branch(repo)
    if not current_branch.startswith(_FEATURE_BRANCH_PREFIX):
        raise CommandException('Please checkout to feature branch')
    return current_branch


command = AggregatedCommand('feature', 'Manages a feature branches.', [
    Command('start', 'Creates a new feature branch.', _start, '<feature name>'),
    Command('publish', 'Publishes a feature branch to review.', _publish),
    Command('finish', 'Closes and pushes a feature to a master branch.', _finish),
    Command('configure', 'Configure feature behaviour.', _configure)
])
