class Command(object):
    def __init__(self, name, description, callable):
        self.name = name
        self.description = description
        self.callable = callable

    def __call__(self, *args, **kwargs):
        return self.callable(*args, **kwargs)

    def nested_commands(self):
        return []

    def __str__(self):
        return '%s\t-\t%s' % (self.name, self.description)


class AggregatedCommand(Command):
    def __init__(self, name, description, commands=[]):
        self.name = name
        self.name
        self.description = description
        self.commands = dict(zip(map(lambda command: command.name, commands), commands))

    def __call__(self, *args, **kwargs):
        if len(args) == 0:
            raise UnknownCommandException("No subcommand specified for command: '%s'" % self.name)
        commandName = args[0]
        if self.commands.get(commandName) is None:
            raise UnknownCommandException("Command '%s' does not contain nested command '%s'" % (self.name, commandName))
        commandArgs = list(args)
        commandArgs.remove(commandName)
        return self.commands.get(commandName)(*commandArgs)

    def add_command(self, command):
        self.commands[command.name] = command

    def nested_commands(self):
        return self.commands.values()


class UnknownCommandException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
