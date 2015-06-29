from git import Repo

from command import AggregatedCommand, Command, CommandException


repo = Repo('.')


def _start_function(feature):
    if feature is None:
        raise CommandException('No feature name given')

    feature_branch = 'feature_%s' % feature

    if repo.heads[feature_branch] is not None:
        raise CommandException("Feature branch '%s' already exists." % feature_branch)

    repo.git.fetch()
    repo.create_head(feature_branch, 'origin/master')
    repo.heads[feature_branch].checkout()


def _finish_function():
    pass


command = AggregatedCommand('feature', 'Manages a feature branches.', [
    Command('start', 'Creates a new feature branch.', _start_function, '<feature name>'),
    Command('finish', 'Closes and pushes a feature to a master branch.', _finish_function)
])
