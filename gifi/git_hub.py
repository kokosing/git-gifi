import getpass
import logging
from github import Github, GithubException
from github.MainClass import DEFAULT_BASE_URL

import feature
from command import AggregatedCommand, Command, CommandException
from gifi.utils.ui import ask
from utils.configuration import Configuration, NOT_SET, configuration_command, REPOSITORY_CONFIG_LEVEL
from utils.git_utils import get_repo, get_remote_url, get_current_branch

PULL_REQUEST_COMMIT_TAG = 'Pull request'


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
    elif error['code'] == 'custom':
        return error['message']
    return error


def _get_github(repo):
    config = _configuration(repo)
    if config.login is NOT_SET:
        raise _missing_configuration_exception('login')
    if config.access_token is NOT_SET:
        raise _missing_configuration_exception('access token')
    return Github(config.access_token, base_url=(_get_github_url(repo)))


def _get_github_url(repo=None):
    target_remote_url = get_remote_url(feature.current(repo).target_remote, repo)
    if 'github.com' not in target_remote_url:
        return 'https://%s/api/v3' % target_remote_url.split('@')[1].split(':')[0]
    else:
        return DEFAULT_BASE_URL


def request(repo=None):
    repo = get_repo(repo)
    try:
        _create_pull_request(repo)
    except GithubException as e:
        _handle_github_exception(e, 'create a pull request')


def _create_pull_request(repo):
    feature_config = feature.configuration(repo)
    f = feature.current(repo)
    working_remote = feature_config.working_remote
    full_repo_name = get_remote_url(f.target_remote, repo).split(':')[1].split('.')[0]
    working_namespace = get_remote_url(working_remote, repo).split(':')[1].split('/')[0]
    current_branch = get_current_branch(repo)

    head = '%s:%s' % (working_namespace, current_branch)
    if f.target_remote is working_remote:
        if current_branch is f.target_branch:
            raise CommandException("Unable to create a pull request from the same remote and branch.")
        head = current_branch

    github = _get_github(repo).get_repo(full_repo_name)
    pull_requests = github.get_pulls('open')
    for pull_request in pull_requests:
        html_url = pull_request.html_url
        if head == pull_request.head.label:
            print "Pull request is already created, see: %s" % html_url
            return

    default_title = repo.head.commit.summary
    title = ask("Title: ", default_title)
    body = ""
    if title is default_title:
        body = repo.head.commit.message
    pull_request_parameters = {
        'title': title,
        'body': body,
        'head': head,
        'base': f.target_branch
    }

    logging.debug('Creating pull request with: %s' % pull_request_parameters)
    pull_request = github.create_pull(**pull_request_parameters)
    print 'Pull request URL: %s' % pull_request.html_url


def _missing_configuration_exception(item):
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
