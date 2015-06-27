from nose.tools import raises

from gifi.command import Command, AggregatedCommand, UnknownCommandException


class TestCallable:
    def __init__(self):
        self.called = False

    def __call__(self, *args, **kwargs):
        self.called = True
        self.args = args
        self.kwargs = kwargs


def test_run_command():
    callable, command = _test_callable('test')
    assert callable.called == False
    command()
    assert callable.called == True
    assert len(command.nested_commands()) == 0


def _test_callable(name):
    callable = TestCallable()
    command = Command(name, 'just a simple test command', callable)
    return callable, command


def test_run_aggregated_command():
    callable1, command1 = _test_callable('test1')
    callable2, command2 = _test_callable('test2')
    command = AggregatedCommand('aggregated', 'description of aggregated command', [command1, command2])
    assert callable1.called == False
    assert callable2.called == False
    command('test1')
    assert callable1.called == True
    assert callable1.args == ()
    assert callable2.called == False
    assert len(command.nested_commands()) == 2


def test_run_aggregated_command_with_args():
    callable1, command1 = _test_callable('test1')
    callable2, command2 = _test_callable('test2')
    command = AggregatedCommand('aggregated', 'description of aggregated command', [command1, command2])
    assert callable1.called == False
    assert callable2.called == False
    command('test1', 'some', 'arg')
    assert callable1.called == True
    assert callable1.args == ('some', 'arg')
    assert callable2.called == False
    assert len(command.nested_commands()) == 2


@raises(UnknownCommandException)
def test_run_aggregated_command_with_wrong_command():
    _, command1 = _test_callable('test1')
    _, command2 = _test_callable('test2')
    command = AggregatedCommand('aggregated', 'description of aggregated command', [command1, command2])
    command('wrong_command')


@raises(UnknownCommandException)
def test_run_aggregated_command_with_no_args():
    _, command1 = _test_callable('test1')
    _, command2 = _test_callable('test2')
    command = AggregatedCommand('aggregated', 'description of aggregated command', [command1, command2])
    command()


def _pdb_break():
    import pdb;

    pdb.set_trace()
