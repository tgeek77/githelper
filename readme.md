# githelper
Tools to make your own private git repos without needing any extra frameworks.

## About:

A lot of use want to create our own private git repos without needing to rely on third-party tools like Github, Gitlab, or even Gitea. If you're concerned about privacy, cloud-based tools always present issues because Terms of Service could change at any time, not to mention the fact that well known services tend to be target for hackers. Even self-hosting a service like Gitea or Gitlab means that you need to worry about the proper care and updates of this software. Often, they have have tons of services that you will never needs.

Instead, what about just using git directly to create and clone repos without needing all of the overhead of these other systems? My scripts do that. They give you a way to quickly create a new repo on a remote machine or even on your local machine, clone the repo that you just created, and start working. These scripts are simple and they each only do one job.

I hope they make your work a little easier if you want to go away from big hosted services.

## SSH

The following scripts are available for servers where your git servers are available remotely and are accessible by ssh.

* `mkrepo.py` will log in to the server with ssh and create the repo in the home directory of the git user.
* `githelper.py` will log in to the server with ssh and provide a list of all current repos. Choose the number of the repo that you want to clone and it will clone it to your current directory.
* `archiverepo.py` will log in to the server with ssh and provide a list of all current repos. Choose the number of the repo that you want to archive. The repo will be backed up as a .tgz file and then the repo directory will be deleted. This is the safe way to delete a repo.
* `rmrepo.py` will log in to the server with ssh and provide a list of all current repos. Choose the number of the repo that you want to delete. The repo is deleted but not backed up first.

## Local

The following scripts are available for local git reposities.  It is assumed that you have created `/srv/git` and you have write permissions to it. The scripts are easy to edit and this directory can be changed to an NFS or SMB share if you don't want to use SSH.

* `mkrepo_local.py` will create the repo in `/srv/git`.
* `githelper_local.py` will provide a list of all current repos in `/srv/git`. Choose the number of the repo that you want to clone and it will clone it to your current directory.
