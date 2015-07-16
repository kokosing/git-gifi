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
    config = configuration(repo)

    if feature is None:
        raise CommandException('No feature name given')

    feature_branch = '%s%s' % (_FEATURE_BRANCH_PREFIX, feature)
    git_utils.check_repo_is_clean(repo)

    if map(lambda head: head.name, repo.heads).count(feature_branch) != 0:
        raise CommandException("Feature branch '%s' already exists." % feature_branch)

    base_branch = config.target_branch
    base_remote = config.target_remote
    if config.start_on_current_branch:
        base_branch = git_utils.get_current_branch(repo)
        base_remote = config.working_remote
    print 'Starting %s on %s/%s.' % (feature_branch, base_remote, base_branch)

    _fetch(repo, config)
    repo.create_head(feature_branch, '%s/%s' % (base_remote, base_branch))
    repo.heads[feature_branch].set_tracking_branch(repo.remotes[base_remote].refs[base_branch])
    repo.heads[feature_branch].checkout()


def _fetch(repo, config):
    try:
        repo.git.fetch(config.target_remote)
        repo.git.fetch(config.working_remote)
    except GitCommandError as e:
        logging.warn('Unable to fetch: %s' % e)
        print 'WARNING: Unable to fetch changes.'


def _publish():
    repo = get_repo()
    check_repo_is_clean(repo)
    config = configuration(repo)
    current_branch = _current_feature_branch(repo)
    repo.git.push('-f', '-u', config.working_remote, 'HEAD:%s' % current_branch)
    if config.publish_with_pull_request:
        git_hub.request(repo)
        _ping(repo)


def _ping(repo=None):
    repo = get_repo(repo)
    reviewers = get_from_last_commit_message(repo, 'Reviewers')
    reviewers = ', '.join(map(lambda r: '<@%s>' % r, reviewers))
    pull_requests = _get_pull_requests(repo)
    if len(pull_requests) > 0:
        message = '%s: Please review: %s' % (reviewers, ','.join(pull_requests))
        slack.notify(message)
    else:
        raise CommandException('No pull request URL in commit message, have you published your feature?')


def _finish():
    repo = get_repo()
    check_repo_is_clean(repo)
    config = configuration(repo)
    _fetch(repo, config)
    interactive = '-i' if config.finish_with_rebase_interactive else ''
    rebase_status = subprocess.call('git rebase %s/%s %s' % (config.target_remote, config.target_branch, interactive), shell=True)
    if rebase_status is not 0:
        raise CommandException('Rebase finished with an error, please fix it manually and then feature-finish once again.')
    repo.git.push(config.target_remote, 'HEAD:%s' % config.target_branch)
    _discard(repo)
    pull_requests = _get_pull_requests(repo)
    if len(pull_requests) > 0:
        slack.notify('%s merged.' % ', '.join(pull_requests))


def _get_pull_requests(repo):
    return get_from_last_commit_message(repo, PULL_REQUEST_COMMIT_TAG)


def _discard(repo=None):
    repo = get_repo(repo)
    config = configuration(repo)
    current_branch = _current_feature_branch(repo)
    repo.git.checkout(config.target_branch)
    repo.git.rebase('%s/%s' % (config.target_remote, config.target_branch))
    try:
        repo.git.commit('--amend', '-C', 'HEAD')
        repo.git.push('-f', '-u', config.working_remote, 'HEAD:%s' % current_branch)
        repo.git.push(config.working_remote, ':%s' % current_branch)
    except GitCommandError as e:
        logging.warn('Unable to drop remote feature branch: %s' % e)
        print 'WARNING: Unable to remove remote feature branch. Maybe it was not yet created?'
    repo.git.branch('-D', current_branch)
    print 'Feature branch was discarded.'


def configuration(repo=None):
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
    current_branch = git_utils.get_current_branch(repo)
    if not current_branch.startswith(_FEATURE_BRANCH_PREFIX):
        raise CommandException('Please checkout to a feature branch.')
    return current_branch


command = AggregatedCommand('feature', 'Manages a feature branches.', [
    Command('start', 'Creates a new feature branch.', _start, '<feature name>'),
    Command('publish', 'Publishes a feature branch to review.', _publish),
    Command('finish', 'Closes and pushes a feature to a target-remote/target-branch.', _finish),
    Command('discard', 'Closes a feature branch without a push to a target-remote/target-branch.', _discard),
    Command('ping', 'Send a notification to reviewers to ask them to do a review.', _ping),
    configuration_command(configuration, 'Configure feature behaviour.')
])
