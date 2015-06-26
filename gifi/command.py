class Command:
    def __init__(self, name, description, callable):
        self.name = name
        self.name
        self.description = description
        self.callable = callable

    def __call__(self, *args, **kwargs):
        self.callable(*args, **kwargs)

    def getNestedCommands(self):
        return []


class AggregatedCommand:
    def __init__(self, name, description, commands):
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
        self.commands.get(commandName)(*commandArgs)

    def nested_commands(self):
        return self.commands


class UnknownCommandException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
