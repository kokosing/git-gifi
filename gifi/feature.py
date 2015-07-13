import git_hub

from utils import git_utils
from utils.configuration import Configuration, configuration_command
from command import AggregatedCommand, Command, CommandException
from utils.git_utils import get_repo, check_repo_is_clean, get_from_last_commit_message
from git_hub import PULL_REQUEST_COMMIT_TAG
import slack

_FEATURE_BRANCH_PREFIX = 'feature_'


def _start(feature=None):
    repo = get_repo()
    config = _configuration(repo)

    if feature is None:
        raise CommandException('No feature name given')

    feature_branch = '%s%s' % (_FEATURE_BRANCH_PREFIX, feature)
    git_utils.check_repo_is_clean(repo)

    if map(lambda head: head.name, repo.heads).count(feature_branch) != 0:
        raise CommandException("Feature branch '%s' already exists." % feature_branch)

    base = 'master'
    if config.start_on_current_branch:
        base = _current_feature_branch(repo)
    print 'Starting %s on origin/%s.' % (feature_branch, base)

    repo.git.fetch()
    repo.create_head(feature_branch, 'origin/%s' % base)
    repo.heads[feature_branch].set_tracking_branch(repo.remotes.origin.refs[base])
    repo.heads[feature_branch].checkout()


def _publish():
    repo = get_repo()
    check_repo_is_clean(repo)
    current_branch = _current_feature_branch(repo)
    repo.git.push('-f', '-u', 'origin', 'HEAD:%s' % current_branch)
    config = _configuration(repo)
    if config.publish_with_pull_request:
        git_hub.request()


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
    pull_requests = get_from_last_commit_message(repo, PULL_REQUEST_COMMIT_TAG)
    if len(pull_requests) > 0:
        slack.notify('%s merged.' % ', '.join(pull_requests))


def _configuration(repo=None):
    repo = get_repo(repo)
    return Configuration(repo, 'feature', {
        'finish-with-rebase-interactive': (False, 'Should do a rebase interactive during feature finishing'),
        'publish-with-pull-request': (False, 'Should create a pull request during feature publishing'),
        'start-on-current-branch': (False, 'Should start a feature branch on current branch (by default it starts on origin/master')
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
    configuration_command(_configuration, 'Configure feature behaviour.')
])
