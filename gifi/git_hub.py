from command import AggregatedCommand, Command, CommandException
from github import Github
from internal.configuration import Configuration
from internal.git_utils import get_repo
import getpass

NOT_SET = 'not-set'


def _authenticate():
    config = _configuration()
    if config.login is NOT_SET:
        config.configure(['login'])
    pw = getpass.getpass('Enter your Github password (will not be stored anywhere): ')
    gh = Github(config.login, pw)
    authorization = gh.get_user().create_authorization(scopes=['repo'], note='git-gifi')
    config.set('access-token', authorization.token)


def _configure():
    _configuration().configure()


def get_github(repo=None):
    config = _configuration(repo)
    if config.login is NOT_SET:
        raise missingConfigurationException('login')
    if config.token is NOT_SET:
        raise missingConfigurationException('access token')
    return Github(config.token)


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
    Command('configure', 'Configure feature behaviour.', _configure)
])
