from unittest import TestCase
from tempfile import mkdtemp
import shutil

from git import Repo
import os
from gifi.feature import command as feature


class AbstractGitReposTest(TestCase):
    def setUp(self):
        self.remote_repo = Repo.init(mkdtemp())
        self.commit_remote_file('init')
        config_writer = self.remote_repo.config_writer()
        config_writer.set_value('receive', 'denyCurrentBranch', 'ignore')

        self.local_repo = Repo.clone_from(self.remote_repo.working_tree_dir, mkdtemp())
        self.old_working_dir = os.getcwd()
        os.chdir(self.local_repo.working_tree_dir)

    def commit_remote_file(self, fileName):
        self.commit_file(self.remote_repo, fileName)

    def commit_local_file(self, fileName):
        self.commit_file(self.local_repo, fileName)

    def commit_file(self, repo, fileName):
        filePath = os.path.join(repo.working_tree_dir, fileName)
        open(filePath, 'w').close()
        repo.index.add([filePath])
        repo.index.commit('Add %s' % filePath)

    def tearDown(self):
        os.chdir(self.old_working_dir)
        shutil.rmtree(self.remote_repo.working_tree_dir)
        shutil.rmtree(self.local_repo.working_tree_dir)


class FutureTest(AbstractGitReposTest):
    def test_happy_path(self):
        assert len(list(self.remote_repo.heads)) == 1
        assert len(list(self.local_repo.heads)) == 1

        feature('start', 'test')
        assert len(list(self.local_repo.heads)) == 2
        assert len(list(self.remote_repo.heads)) == 1

        self.commit_local_file('feature_test_file')
        feature('publish')
        assert len(list(self.local_repo.heads)) == 2
        assert len(list(self.remote_repo.heads)) == 2

        assert len(os.listdir(self.remote_repo.working_tree_dir)) == 2
        self.remote_repo.heads.feature_test.checkout()
        assert len(os.listdir(self.remote_repo.working_tree_dir)) == 3
        self.remote_repo.heads.master.checkout()
        assert len(os.listdir(self.remote_repo.working_tree_dir)) == 2

        feature('finish')
        self.remote_repo.head.reset(index=True, working_tree=True)
        assert len(list(self.local_repo.heads)) == 1
        assert len(list(self.remote_repo.heads)) == 1
        assert len(os.listdir(self.remote_repo.working_tree_dir)) == 3
