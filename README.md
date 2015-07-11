# git-gifi

[![travis](https://api.travis-ci.org/kokosing/git-gifi.svg)](https://travis-ci.org/kokosing/git-gifi/)

Git and github enhancements to git.

***
##Requirmentes:

-  git (tested with version 1.9.1)
-  python 2.7

##Installation

In order to install git-gifi please do the following (usage of virutalevn is recommend):

	pip install git-gifi
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

###Github
To use github integration you need to authoriize first (obtain an access token):

	git github-authorize
	
Note that authorization information are stored per repository. Thanks to that it is possible to work with different github providers like github.com or github enterprise. However, if you have multiple repositories on the same github providers then you won't be able to authenticate git-gifi again, as it is already authenticated for different reposotiry but same github provider. In that case you need to go to your github profile settings, copy git-gifi access token and us it in below command:

	git github-configure
	
##### Pull request
With **git github-request** you can post a new pull request from current branch. It is required that branch is not 'master' and it is already pushed.
In order to create a pull request during **git feature-publish**, please do **git feature-configure** first and enable pull request creation.

###Slack
To use github integration you need to authenticate first obtain an access token for slack web api and the pass it to:

	git slack-configure

By default when you run ``*-configure``` command configuration is stored in local repository. Typically slack configuration does not change between projects, so in order to store it globally (system wide) you can run below command. Thanks to that slack configuration will be reused between git repositories on your system:

	git slack-configure global
	
	
##### Notify about pull request changes
If you want to send a notifaction to slack channel about pull request changes you need to enable it by specifying the channel to which you want to send messages.

	git slack-configure
	
Additinally, if you want to send notification to particular people on slack like: mike and john, then add below line to your last commit message in pull request:

	Reviewers: mike, john


