import logging
import subprocess
from git import GitCommandError

import epic
import git_hub
import slack
from command import AggregatedCommand, Command, CommandException
from git_hub import PULL_REQUEST_COMMIT_TAG
from utils import git_utils
from utils.configuration import Configuration, configuration_command
from utils.git_utils import get_repo, check_repo_is_clean, get_from_last_commit_message


def _start(feature=None):
    repo = get_repo()

    if feature is None:
        raise CommandException('No feature name given')

    (target_remote, target_branch) = epic.current()
    feature_branch = '%s/%s/%s' % (target_remote, target_branch, feature)
    git_utils.check_repo_is_clean(repo)

    if map(lambda head: head.name, repo.heads).count(feature_branch) != 0:
        raise CommandException("Feature branch '%s' already exists." % feature_branch)

    print 'Starting %s on %s/%s.' % (feature_branch, target_remote, target_branch)

    _fetch(repo, target_remote)
    repo.create_head(feature_branch, '%s/%s' % (target_remote, target_branch))
    repo.heads[feature_branch].set_tracking_branch(repo.remotes[target_remote].refs[target_branch])
    repo.heads[feature_branch].checkout()


def _fetch(repo, remote):
    try:
        repo.git.fetch(remote)
    except GitCommandError as e:
        logging.warn('Unable to fetch: %s' % e)
        print 'WARNING: Unable to fetch changes.'


def _publish():
    repo = get_repo()
    check_repo_is_clean(repo)
    config = configuration(repo)
    _push_working_branch(config, repo)
    if config.publish_with_pull_request:
        git_hub.request(repo)


def _push_working_branch(config, repo):
    current_branch = _current_feature_branch(repo)
    push_params = [config.working_remote, 'HEAD:%s' % current_branch]
    try:
        repo.git.push('-u', *push_params)
    except GitCommandError as e:
        logging.warn('Unable push (publish) feature branch without force: %s' % e)
        message = 'Unable to push your changes ("git push -u %s %s"). Would you like to use force?'
        question = message % tuple(push_params)
        if ask(question):
            repo.git.push('-f', '-u', *push_params)
        else:
            raise CommandException('Manual pull and rebase is required')


def ask(question):
    while True:
        answer = raw_input('%s [yes|no]: ' % question).strip().lower()
        if answer == 'yes':
            return True
        elif answer == 'no':
            return False


def _finish():
    repo = get_repo()
    check_repo_is_clean(repo)
    config = configuration(repo)
    _current_feature_branch(repo)
    (target_remote, target_branch, feature_name) = current(repo)
    _fetch(repo, target_remote)
    interactive = '-i' if config.finish_with_rebase_interactive else ''
    rebase_cmd = 'git rebase %s/%s %s' % (target_remote, target_branch, interactive)
    rebase_status = subprocess.call(rebase_cmd, shell=True)
    if rebase_status is not 0:
        message = 'Rebase finished with an error, please fix it manually and then feature-finish once again.'
        raise CommandException(message)
    _push_working_branch(config, repo)
    repo.git.push(target_remote, 'HEAD:%s' % target_branch)
    _discard()
    pull_requests = _get_pull_requests(repo)
    if len(pull_requests) > 0:
        slack.notify('%s merged.' % ', '.join(pull_requests))


def _get_pull_requests(repo):
    return get_from_last_commit_message(repo, PULL_REQUEST_COMMIT_TAG)


def _discard():
    repo = get_repo()
    config = configuration(repo)
    feature_branch = _current_feature_branch(repo)
    (target_remote, target_branch, feature_name) = current(repo)
    repo.git.checkout(target_branch)
    try:
        repo.git.push(config.working_remote, ':%s' % feature_branch)
    except GitCommandError as e:
        logging.warn('Unable to drop remote feature branch: %s' % e)
        print 'WARNING: Unable to remove remote feature branch. Maybe it was not yet created?'
    repo.git.branch('-D', feature_branch)
    repo.git.rebase('%s/%s' % (target_remote, target_branch))
    repo.git.fetch('%s' % config.working_remote, '--prune')


def configuration(repo=None):
    repo = get_repo(repo)
    return Configuration(repo, 'feature', {
        'finish-with-rebase-interactive': (False, 'Should do a rebase interactive during feature finishing'),
        'publish-with-pull-request': (False, 'Should create a pull request during feature publishing'),
        'working-remote': ('origin', 'On which remote you are working at')
    })


def _current_feature_branch(repo):
    current_branch = git_utils.get_current_branch(repo)
    if not current_branch.count('/') > 1:
        raise CommandException('Please checkout to a feature branch.')
    return current_branch


def current(repo):
    parts = _current_feature_branch(repo).split('/')
    target_remote = parts[0]
    target_branch = '/'.join(parts[1:-1])
    feature = parts[-1]
    return (target_remote, target_branch, feature)


command = AggregatedCommand('feature', 'Manages a feature branches.', [
    Command('start', 'Creates a new feature branch.', _start, '<feature name>'),
    Command('publish', 'Publishes a feature branch to review.', _publish),
    Command('finish', 'Closes and pushes a feature to a feature epic branch.', _finish),
    Command('discard', 'Closes a feature branch without a push.', _discard),
    configuration_command(configuration, 'Configure feature behaviour.')
])
