import sys

from internal import git_utils
from command import Command, AggregatedCommand, UnknownCommandException, CommandException
import feature
import queue

command = AggregatedCommand('gifi', 'Git and github enhancements to git.', [
    feature.command,
    queue.command
])


class HelpGenerator(object):
    def __init__(self, main):
        self.main = main

    def __call__(self):
        help = str(self.main)
        help += '\nUsage:\n\t%s command [command arguments]\n\nCommands:\n' % self.main.name

        # it does not have to be recursive as there are only two levels
        for command in self.main.nested_commands():
            help += str(command)
            if len(command.nested_commands()) != 0:
                help += ' See below subcommands:\n'
                for subcommand in command.nested_commands():
                    help += '\t%s\n' % str(subcommand)
            help += '\n'

        return help


command.add_command(Command('help', 'Display this window.', HelpGenerator(command)))


class AliasesInstaller(object):
    def __init__(self, main):
        self.main = main

    def __call__(self):
        repo = git_utils.get_repo()
        config_writer = repo.config_writer()
        # it does not have to be recursive as there are only two levels
        for command in self.main.nested_commands():
            if len(command.nested_commands()) != 0:
                for subcommand in command.nested_commands():
                    alias = '%s-%s' % (command.name, subcommand.name)
                    config_writer.set_value('alias', alias, '"!%s %s %s $*"' % (sys.argv[0], command.name, subcommand.name))
        config_writer.release()


command.add_command(Command('install', 'Install gifi as git bunch of aliases.', AliasesInstaller(command)))


def main():
    args = list(sys.argv)
    args.pop(0)
    _main(args)


def _main(args):
    if len(args) == 0:
        args.append('help')
    try:
        result = command(*args)
        if result is not None:
            print result
    except UnknownCommandException:
        print "Wrong command, try 'help'."
    except CommandException as e:
        print "ERROR: %s" % e
