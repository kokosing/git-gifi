class Command(object):
    def __init__(self, name, description, callable, args=None):
        self.name = name
        self.description = description
        self.callable = callable
        self.args = args

    def __call__(self, *args, **kwargs):
        return self.callable(*args, **kwargs)

    def nested_commands(self):
        return []

    def __str__(self):
        args = ''
        if self.args is not None:
            args = ' %s' % self.args
        else:
            args = '\t'
        return '%s%s\t-\t%s' % (self.name, args, self.description)


class AggregatedCommand(Command):
    def __init__(self, name, description, commands=[]):
        super(AggregatedCommand, self).__init__(name, description, None)
        self.commands = dict(zip(map(lambda command: command.name, commands), commands))

    def __call__(self, *args, **kwargs):
        if len(args) == 0:
            raise UnknownCommandException("No subcommand specified for command: '%s'" % self.name)
        commandName = args[0]
        if self.commands.get(commandName) is None:
            raise UnknownCommandException(
                "Command '%s' does not contain nested command '%s'" % (self.name, commandName))
        commandArgs = list(args)
        commandArgs.remove(commandName)
        return self.commands.get(commandName)(*commandArgs)

    def add_command(self, command):
        self.commands[command.name] = command

    def nested_commands(self):
        return self.commands.values()

    def __str__(self):
        subcommand = ''
        if self.nested_commands() != 0:
            subcommand = ' <subcommand>'
        return '%s%s\t-\t%s' % (self.name, subcommand, self.description)


class CommandException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnknownCommandException(CommandException):
    def __init__(self, value):
        super(UnknownCommandException, self).__init__(value)
