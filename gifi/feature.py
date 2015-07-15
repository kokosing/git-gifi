import logging
import subprocess

from git import GitCommandError

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

    base_branch = config.target_branch
    base_remote = config.target_remote
    if config.start_on_current_branch:
        base_branch = git_utils.current_branch(repo)
        base_remote = config.working_remote
    print 'Starting %s on %s/%s.' % (feature_branch, base_remote, base_branch)

    _fetch(repo)
    repo.create_head(feature_branch, '%s/%s' % (base_remote, base_branch))
    repo.heads[feature_branch].set_tracking_branch(repo.remotes[base_remote].refs[base_branch])
    repo.heads[feature_branch].checkout()


def _fetch(repo):
    try:
        repo.git.fetch()
    except GitCommandError as e:
        logging.warn('Unable to fetch: %s' % e)
        print 'WARNING: Unable to fetch changes.'


def _publish():
    repo = get_repo()
    check_repo_is_clean(repo)
    config = _configuration(repo)
    current_branch = _current_feature_branch(repo)
    repo.git.push('-f', '-u', config.working_remote, 'HEAD:%s' % current_branch)
    if config.publish_with_pull_request:
        git_hub.request(config.target_branch, repo)


def _finish():
    repo = get_repo()
    check_repo_is_clean(repo)
    config = _configuration(repo)
    repo.git.fetch()
    interactive = '-i' if config.finish_with_rebase_interactive else ''
    rebase_status = subprocess.call('git rebase %s/%s %s' % (config.target_remote, config.target_branch, interactive), shell=True)
    if rebase_status is not 0:
        raise CommandException('Rebase finished with an error, please fix it manually and then feature-finish once again.')
    repo.git.push(config.target_remote, 'HEAD:%s' % config.target_branch)
    _discard(repo)
    pull_requests = get_from_last_commit_message(repo, PULL_REQUEST_COMMIT_TAG)
    if len(pull_requests) > 0:
        slack.notify('%s merged.' % ', '.join(pull_requests))


def _discard(repo=None):
    repo = get_repo(repo)
    config = _configuration(repo)
    current_branch = _current_feature_branch(repo)
    repo.git.checkout(config.target_branch)
    repo.git.rebase('%s/%s' % (config.target_remote, config.target_branch))
    try:
        repo.git.push(config.working_remote, ':%s' % current_branch)
    except GitCommandError as e:
        logging.warn('Unable to drop remote feature branch: %s' % e)
        print 'WARNING: Unable to remove remote feature branch. Maybe it was not yet created?'
    repo.git.branch('-D', current_branch)
    print 'Feature branch was discarded.'


def _configuration(repo=None):
    repo = get_repo(repo)
    return Configuration(repo, 'feature', {
        'finish-with-rebase-interactive': (False, 'Should do a rebase interactive during feature finishing'),
        'publish-with-pull-request': (False, 'Should create a pull request during feature publishing'),
        'start-on-current-branch': (False, 'Should start a feature branch on current branch, by default it starts on target-remote/target-branch'),
        'working-remote': ('origin', 'On which remote you are working at'),
        'target-remote': ('origin', 'To which remote your work is going to be eventually pushed'),
        'target-branch': ('master', 'Branch on target-remote on which your feature is basing')
    })


def _current_feature_branch(repo):
    current_branch = git_utils.current_branch(repo)
    if not current_branch.startswith(_FEATURE_BRANCH_PREFIX):
        raise CommandException('Please checkout to a feature branch.')
    return current_branch


command = AggregatedCommand('feature', 'Manages a feature branches.', [
    Command('start', 'Creates a new feature branch.', _start, '<feature name>'),
    Command('publish', 'Publishes a feature branch to review.', _publish),
    Command('finish', 'Closes and pushes a feature to a target-remote/target-branch.', _finish),
    Command('discard', 'Closes a feature branch without a push to a target-remote/target-branch.', _discard),
    configuration_command(_configuration, 'Configure feature behaviour.')
])
