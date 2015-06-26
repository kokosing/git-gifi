from gifi.command import Command

class TestCallable:
    def __init__(self):
        self.called = False

    def __call__(self, *args, **kwargs):
        self.called = True

def test_run_command():
    lambda_called = False
    callable = TestCallable()
    command = Command('test', 'just a simple test command', callable)
    command()
    assert callable.called == True
