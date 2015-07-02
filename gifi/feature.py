from git import Repo

from internal import git_utils
from internal.configuration import Configuration

from command import AggregatedCommand, Command, CommandException
from internal.git_utils import get_repo

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
    current_branch = _current_feature_branch(repo)
    repo.git.push('-u', 'origin', 'HEAD:%s' % current_branch)


def _finish():
    repo = get_repo()
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
        'finish-with-rebase-interactive': (False, 'Should do a rebase interactive during feature finishing')
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
