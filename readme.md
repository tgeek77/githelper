# githelper
Tools to make your own private git repos without needing any extra frameworks.

## About:

A lot of use want to create our own private git repos without needing to rely on third-party tools like Github, Gitlab, or even Gitea. If you're concerned about privacy, cloud-based tools always present issues because Terms of Service could change at any time, not to mention the fact that well known services tend to be target for hackers. Even self-hosting a service like Gitea or Gitlab means that you need to worry about the proper care and updates of this software. Often, they have have tons of services that you will never needs.

Instead, what about just using git directly to create and clone repos without needing all of the overhead of these other systems? My scripts do that. They give you a way to quickly create a new repo on a remote machine or even on your local machine, clone the repo that you just created, and start working. These scripts are simple and they each only do one job.

I hope they make your work a little easier if you want to go away from big hosted services.

## Update:

I guess you can call this version 1.0 of the githelper ssh script. I have integrated all of the individual scripts into a single script that does everything and it works using command line tags. Right now you need to define the user and server every time. 

## Todos:
* My next task will be finding a way to define that once so that it does not ask you again. You can also use githelper now with other scripts to define this. So if you like it you could predefine everything using a simple bash script or you can hardcode everything yourself in the githelper python script.
* I'll also create a unified offline script for people who want to use a local repository and I'll also allow it to ask you where you want to save the repo instead of always being `/opt/git` by default.