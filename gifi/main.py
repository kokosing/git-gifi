import sys

from command import Command, AggregatedCommand, UnknownCommandException, CommandException
import feature
import queue


class HelpGenerator(object):
    def __init__(self, main):
        self.main = main

    def __call__(self, *args, **kwargs):
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


command = AggregatedCommand('gifi', 'Git and github enhancements to git.', [
    feature.command,
    queue.command
])
_help = Command('help', 'display this window.', HelpGenerator(command))
command.add_command(_help)


def main():
    args = list(sys.argv)
    args.pop(0)
    _main(args)


def _main(args):
    if len(args) == 0:
        args.append('help')
    try:
        print command(*args)
    except UnknownCommandException:
        print "Wrong command, try 'help'."
    except CommandException as e:
        print "ERROR: %s" + str(e)
