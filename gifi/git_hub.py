import getpass

from github import Github
from command import AggregatedCommand, Command, CommandException
from utils.configuration import Configuration, NOT_SET, configuration_command
from utils.git_utils import get_repo, remote_origin_url, current_branch, get_from_last_commit_message
import slack

PULL_REQUEST_COMMIT_TAG = 'Pull request:'


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


def request(repo=None):
    repo = get_repo(repo)
    cur_branch = current_branch(repo)
    if cur_branch is 'master':
        raise CommandException("Unable to create a pull request from 'master'")

    origin_url = remote_origin_url(repo)
    full_repo_name = origin_url.split(':')[1].split('.')[0]

    pull = get_github(repo).get_repo(full_repo_name).create_pull(
        title=repo.head.commit.summary,
        body=repo.head.commit.message,
        head=cur_branch,
        base='master'
    )
    repo.git.commit('--amend', '-m', '%s\n\n%s %s' % (repo.head.commit.message, PULL_REQUEST_COMMIT_TAG, pull.html_url))
    print 'Pull request URL: %s' % pull.html_url

    channel = _configuration(repo).slack_pr_notification_channel
    if channel is not NOT_SET:
        reviewers = get_from_last_commit_message(repo, 'Reviewers:')
        message = '%s Please review: %s' % (', '.join(map(lambda r: '@%s' % r, reviewers)), pull.html_url)
        slack.notify(channel, message)


def missingConfigurationException(item):
    return CommandException('No github %s is set, please do configure or authenticate github first.' % item)


def _configuration(repo=None):
    repo = get_repo(repo)
    return Configuration(repo, 'github', {
        'login': (NOT_SET, 'Github login'),
        'access-token': (NOT_SET, 'Github access token')
    })


command = AggregatedCommand('github', 'Integration with github.', [
    Command('authenticate', 'Authenticate and retrieve github access token.', _authenticate),
    Command('request', 'Creates a pull request from current branch.', request),
    configuration_command(_configuration, 'Configure github settings.')
])
