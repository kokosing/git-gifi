import getpass
import logging

from github import Github, GithubException
from command import AggregatedCommand, Command, CommandException
from github.MainClass import DEFAULT_BASE_URL
from utils.configuration import Configuration, NOT_SET, configuration_command, REPOSITORY_CONFIG_LEVEL
from utils.git_utils import get_repo, remote_origin_url, current_branch, get_from_last_commit_message
import slack

PULL_REQUEST_COMMIT_TAG = 'Pull request:'


def _authorize(config_level=REPOSITORY_CONFIG_LEVEL):
    config = _configuration()
    if config.login is NOT_SET:
        config.configure(config_level, keys=['login'])
    pw = getpass.getpass('Enter your Github password (will not be stored anywhere): ')
    gh = Github(config.login, pw, base_url=_get_github_url())
    _create_authorization(config, config_level, gh)


def _create_authorization(config, config_level, gh):
    try:
        authorization = gh.get_user().create_authorization(scopes=['repo'], note='git-gifi')
        config.set('access-token', authorization.token, config_level)
    except GithubException as e:
        _handle_github_exception(e, 'create an authorization')


def _handle_github_exception(e, event):
    logging.warn('%s raised an exception: %s' % (event, e))
    if 'errors' in e.data:
        error = ', '.join(map(_map_github_error, e.data['errors']))
    else:
        error = e.data['message']
    raise CommandException('Unable to %s: %s' % (event, error))


def _map_github_error(error):
    if error['code'] == 'already_exists':
        return 'Authorization already exists, copy paste existing token and use it in configure command.'
    return error


def get_github(repo):
    config = _configuration(repo)
    if config.login is NOT_SET:
        raise missingConfigurationException('login')
    if config.access_token is NOT_SET:
        raise missingConfigurationException('access token')
    return Github(config.access_token, base_url=(_get_github_url(repo)))


def _get_github_url(repo=None):
    origin_url = remote_origin_url(repo)
    if 'github.com' not in origin_url:
        return 'https://%s/api/v3' % origin_url.split('@')[1].split(':')[0]
    else:
        return DEFAULT_BASE_URL


def request(repo=None):
    repo = get_repo(repo)

    try:
        pull = _create_pull_request(repo)
    except GithubException as e:
        _handle_github_exception(e, 'create a pull request')

    repo.git.commit('--amend', '-m', '%s\n\n%s %s' % (repo.head.commit.message, PULL_REQUEST_COMMIT_TAG, pull.html_url))
    print 'Pull request URL: %s' % pull.html_url

    reviewers = get_from_last_commit_message(repo, 'Reviewers:')
    message = '%s Please review: %s' % (', '.join(map(lambda r: '@%s' % r, reviewers)), pull.html_url)
    slack.notify(message)


def _create_pull_request(repo):
    origin_url = remote_origin_url(repo)
    full_repo_name = origin_url.split(':')[1].split('.')[0]
    cur_branch = current_branch(repo)
    if cur_branch is 'master':
        raise CommandException("Unable to create a pull request from 'master' branch.")
    pull = get_github(repo).get_repo(full_repo_name).create_pull(
        title=repo.head.commit.summary,
        body=repo.head.commit.message,
        head=cur_branch,
        base='master'
    )
    return pull


def missingConfigurationException(item):
    return CommandException('No github %s is set, please do configure or authorize github first.' % item)


def _configuration(repo=None):
    repo = get_repo(repo)
    return Configuration(repo, 'github', {
        'login': (NOT_SET, 'Github login'),
        'access-token': (NOT_SET, 'Github access token')
    })


command = AggregatedCommand('github', 'Integration with github.', [
    Command('authorize', 'Create authorization and retrieve github access token.', _authorize),
    Command('request', 'Creates a pull request from current branch.', request),
    configuration_command(_configuration, 'Configure github settings.')
])
