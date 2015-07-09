import getpass

from github import Github

from command import AggregatedCommand, Command, CommandException
from internal.configuration import Configuration, NOT_SET, configuration_command
from internal.git_utils import get_repo, remote_origin_url


def _authenticate():
    config = _configuration()
    if config.login is NOT_SET:
        config.configure(['login'])
    pw = getpass.getpass('Enter your Github password (will not be stored anywhere): ')
    gh = Github(config.login, pw, base_url=_get_github_url())
    authorization = gh.get_user().create_authorization(scopes=['repo'], note='git-gifi')
    config.set('access-token', authorization.token)


def get_github(repo):
    config = _configuration(repo)
    if config.login is NOT_SET:
        raise missingConfigurationException('login')
    if config.access_token is NOT_SET:
        raise missingConfigurationException('access token')
    return Github(config.access_token, base_url=(_get_github_url(repo)))


def _get_github_url(repo=None):
    origin_url = remote_origin_url(repo)
    github_url = None
    if 'github.com' not in origin_url:
        github_url = 'https://%s/api/v3' % origin_url.split('@')[1].split(':')[0]
        print 'Using github URL: %s' % github_url
    return github_url


def missingConfigurationException(item):
    return CommandException('No github %s is set, please do configure or authenticate github first.' % item)


def _configuration(repo=None):
    repo = get_repo(repo)
    return Configuration(repo, 'github', {
        'login': (NOT_SET, 'Github login'),
        'access-token': (NOT_SET, 'Github access token')
    })


command = AggregatedCommand('github', 'Integration with github.', [
    Command('authenticate', 'Creates a new feature branch.', _authenticate),
    configuration_command(_configuration, 'Configure github settings.')
])
