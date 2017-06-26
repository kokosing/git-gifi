git-gifi
========

|travis|

Git and github enhancements to git.

--------------

Requirmentes:
-------------

-  git (tested with version 1.9.1)
-  python 2.7

Installation
------------

In order to install git-gifi please do the following (usage of virutalevn is recommend):

::

    pip install git-gifi
    # if you prefer to gifi via set of git aliases, then
    gifi install

Usage
-----

Queue
~~~~~

Concept of queue comes from `Mercurial
Queues <http://hgbook.red-bean.com/read/managing-change-with-mercurial-queues.html>`__. However this
implementation is much simplier (git stash based). You can push (with **gifi push**) your commit on
the queue (into git stash) and then pop (with **git pop**) it from the queue to your workspace.

Feature
~~~~~~~

It is a simplified version of
`gitflow <https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow>`__. It is
well suited to the case where you and your team work always on the same branch called *master* (no
*develop* branch). For each feature you create a *feature branch* wich then is merged into *master*.
Releases are just tagged commits in *master*.

::

    git feature-start new_feature
    git add new_feature.code
    git commit  -m 'new feature commit message'
    git feature-publish
    # after code review
    git feature-finish

Note that in case you have no permission to push into *target-remote* and somebody merged your
commit to *target-remote*, then you may want to use just *feature-discard* to clean your
*working-remote*.

Github
~~~~~~

To use github integration you need to authoriize first (obtain an access token):

::

    git github-authorize

Note that authorization information are stored per repository. Thanks to that it is possible to work
with different github providers like github.com or github enterprise. However, if you have multiple
repositories on the same github providers then you won't be able to authenticate git-gifi again, as
it is already authenticated for different reposotiry but same github provider. In that case you need
to go to your github profile settings, copy git-gifi access token and us it in below command:

::

    git github-configure

Pull request
''''''''''''

With **git github-request** you can post a new pull request from current branch. It is required that
branch is not 'master' and it is already pushed. In order to create a pull request during **git
feature-publish**, please do **git feature-configure** first and enable pull request creation.

Epics - working with forked project or with long lasting feature branches
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section is particularly useful in case you are working on a forked project (*you/Project*) and
you want to create pull requests in project you forked from (*they/Project*). So to make
**git-gifi** be able to create pull request you have to have both projects remotes added to your
repositiory. Then you can use **git epic-add** to add a remote/branch on with which you are going to
work with, then every time you do **git feature-start**, you will be asked to select an epic
(remote/branch) on which your new feature will based on and against which you will create a pull
request.

.. |travis| image:: https://api.travis-ci.org/kokosing/git-gifi.svg
   :target: https://travis-ci.org/kokosing/git-gifi/
