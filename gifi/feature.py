from git import Repo

from command import AggregatedCommand, Command, CommandException


repo = Repo('.')


def _start(feature):
    if feature is None:
        raise CommandException('No feature name given')

    feature_branch = 'feature_%s' % feature
    if repo.is_dirty():
        raise CommandException('Please commit all untracked files before creating a feature branch')

    if map(lambda head: head.name, repo.heads).count(feature_branch) != 0:
        raise CommandException("Feature branch '%s' already exists." % feature_branch)

    repo.git.fetch()
    repo.create_head(feature_branch, 'origin/master')
    repo.heads[feature_branch].checkout()


def _finish():
    raise CommandException("Not implemented yet")


command = AggregatedCommand('feature', 'Manages a feature branches.', [
    Command('start', 'Creates a new feature branch.', _start, '<feature name>'),
    Command('finish', 'Closes and pushes a feature to a master branch.', _finish)
])
