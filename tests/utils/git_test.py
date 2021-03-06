import shutil
from tempfile import mkdtemp
from unittest import TestCase

from git import Repo
import os


class AbstractGitReposTest(TestCase):
    def setUp(self):
        self.remote_repo = Repo.init(mkdtemp())
        self.commit_remote_file('init')
        config_writer = self.remote_repo.config_writer()
        config_writer.set_value('receive', 'denyCurrentBranch', 'ignore')
        config_writer.set_value('receive', 'denyDeleteCurrent', 'ignore')
        config_writer.release()

        self.local_repo = Repo.clone_from(self.remote_repo.working_tree_dir, mkdtemp())
        self.old_working_dir = os.getcwd()
        os.chdir(self.local_repo.working_tree_dir)

    def tearDown(self):
        os.chdir(self.old_working_dir)
        shutil.rmtree(self.remote_repo.working_tree_dir)
        shutil.rmtree(self.local_repo.working_tree_dir)

    def commit_remote_file(self, fileName, commit_message=None):
        self.commit_file(self.remote_repo, fileName, commit_message)

    def commit_local_file(self, fileName, commit_message=None):
        self.commit_file(self.local_repo, fileName, commit_message)

    def commit_file(self, repo, fileName, commit_message=None):
        filePath = os.path.join(repo.working_tree_dir, fileName)
        open(filePath, 'w').close()
        repo.index.add([filePath])
        if commit_message is None:
            commit_message = 'Add %s' % filePath
        repo.index.commit(commit_message)

    def remote_files_count(self, branch = 'master'):
        self.remote_repo.heads[branch].checkout()
        self.remote_repo.head.reset(index=True, working_tree=True)
        return len(os.listdir(self.remote_repo.working_tree_dir))

    def remote_heads_count(self):
        return len(list(self.remote_repo.heads))

    def local_files_count(self):
        return len(os.listdir(self.local_repo.working_tree_dir))

    def local_heads_count(self):
        return len(list(self.local_repo.heads))
