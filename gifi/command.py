class Command:
    def __init__(self, name, description, callable):
        self.name = name
        self.name
        self.description = description
        self.callable = callable

    def __call__(self, *args, **kwargs):
        self.callable(args, kwargs)
