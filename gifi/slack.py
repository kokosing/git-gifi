from slackclient import SlackClient

from command import AggregatedCommand, Command, CommandException
from utils.configuration import Configuration, NOT_SET, configuration_command
from utils.git_utils import get_repo

_SLACK_MESSAGE_SUFFIX = '(sent via git-gifi)'


def _configuration(repo=None):
    repo = get_repo(repo)
    return Configuration(repo, 'slack', {
        'access-token': (NOT_SET, 'Slack access token'),
        'notification-channel': (NOT_SET, 'Slack channel to where notification will be send')
    })


def notify(message):
    config = _configuration()
    if config.notification_channel is NOT_SET:
        raise missingConfigurationException('notification-channel')
    if config.access_token is NOT_SET:
        raise missingConfigurationException('access-token')
    client = SlackClient(config.access_token)
    message = '%s %s' % (message, _SLACK_MESSAGE_SUFFIX)
    channel = '#%s' % config.notification_channel
    client.api_call('chat.postMessage', channel=channel, text=message, as_user=True, parse='full')


def missingConfigurationException(item):
    return CommandException('No slack %s is set, please do configure.' % item)


command = AggregatedCommand('slack', 'Integration with slack.', [
    Command('notify', 'Post a message on given channel.', notify, '<message>'),
    configuration_command(_configuration, 'Configure slack settings.')
])
