# git-gifi

[![travis](https://api.travis-ci.org/kokosing/git-gifi.svg)](https://travis-ci.org/kokosing/git-gifi/)

Git and github enhancements to git.

***
##Requirmentes:

-  git (tested with version 1.9.1)
-  python 2.7

##Installation

In order to install git-gifi please do the following:

	sudo apt-get install python-dev
	git clone git@github.com:kokosing/git-gifi.git
	cd git-gifi
	virtualenv virtual-env
	source virtual-env/bin/activate
	python setup.py install
	# if you prefer to gifi via set of git aliases, then
	gifi install

##Usage
###Queue
Concept of queue comes from [Mercurial Queues](http://hgbook.red-bean.com/read/managing-change-with-mercurial-queues.html). However this implementation is much simplier (git stash based). You can push (with **gifi push**) your commit on the queue (into git stash) and then pop (with **git pop**) it from the queue to your workspace.

###Feature
It is a simpliified version of [gitflow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow). It is well suited to the case where you and your team work always on the same branch called *master* (no *develop* branch). For each feature you create a *feature branch* wich then is merged into *master*. Releases are just tagged commits in *master*.

	git feature-start new_feature
	git add new_feature.code
	git commit  -m 'new feature commit message'
	git feature-publish
	# after code review
	git feature-finish

In near future **git feature-publish** will create a pull request in github.


