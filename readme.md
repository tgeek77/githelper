# githelper
Tools to make your own private git repos without needing any extra frameworks.

## About:

A lot of use want to create our own private git repos without needing to rely on third-party tools like Github, Gitlab, or even Gitea. If you're concerned about privacy, cloud-based tools always present issues because Terms of Service could change at any time, not to mention the fact that well known services tend to be target for hackers. Even self-hosting a service like Gitea or Gitlab means that you need to worry about the proper care and updates of this software. Often, they have have tons of services that you will never needs.

Instead, what about just using git directly to create and clone repos without needing all of the overhead of these other systems? My scripts do that. They give you a way to quickly create a new repo on a remote machine or even on your local machine, clone the repo that you just created, and start working. These scripts are simple and they each only do one job.

I hope they make your work a little easier if you want to go away from big hosted services.

## How to use githelper:

githelper.py allows you to use any ssh connection as a place to store git repositories. This can be on a raspberry pi in your own home or it could be on a server in another country. As long as you have SSH access to that device, githelper.py will be able to work with it.

githelper_local.py works the same way excect it will use any directory on your local computer. This directory can be on your local filesystem, a USB Drive, or a network share like NFS. 

```
usage: githelper.py [-h] [--server SERVER] [--user USER] [--list] [--clone CLONE] [--new NEW] [--archive ARCHIVE] [--remove REMOVE] 
                    [--port PORT] [--rename] [--fork] [--oldrepo OLDREPO] [--newrepo NEWREPO] [--dir DIR]

A simple script with multiple command-line flags.

options:
  -h, --help            show this help message and exit
  --server SERVER       What server should I use?
  --user USER           What user should I use?
  --list, -l            Lists existing repos
  --clone CLONE, -c CLONE
                        Clones a repo locally
  --new NEW, -n NEW     Create a new repo
  --archive ARCHIVE, -a ARCHIVE
                        Compresses a repo into a tarball file
  --remove REMOVE       Deletes a repo
  --port PORT, -p PORT  Set the ssh port to something other than 22
  --rename, -rn         Rename repo
  --fork, -f            Copy repo
  --oldrepo OLDREPO     Old Name (Used with fork or rename)
  --newrepo NEWREPO     New Name (Used with fork or rename)
  --dir DIR, -d DIR     Set the directory where your git repos are located on the server

```
usage: githelper_local.py [-h] [--loc LOC] [--list] [--clone CLONE] [--new NEW]
                          [--archive ARCHIVE]

A simple script with multiple command-line flags.

options:
  -h, --help            show this help message and exit
  --loc LOC             What location should I use?
  --list, -l            Lists existing repos
  --clone CLONE, -c CLONE
                        Clones a repo locally
  --new NEW, -n NEW     Create a new repo
  --archive ARCHIVE, -a ARCHIVE
                        Compresses a repo into a tarball file
```

### Note on Cloning:
The clone function can seem like it froze up if the repository that you are cloning is very large and you connection is slow.

## Update:
- Added rename and fork functions.
  - Rename will rename the repository on the server, you will need to re-clone the repo or manually change the upstream repo url in your local repo.
  - Fork will copy an existing repository on the server to a new name. You can then clone the fork to a new local repo. The original and the fork will have no relation so if you decide to merge them again in the future, that will need to be done manually.

- aliases.md contains a few BASH aliases that you can use with githelper. I thought long a hard about writing a function into githelper that would cache your settings so you don't have to write them manually every time. I think wrapping a simple alias around the command is a better way to go.

There is one more option if you don't want to use aliases:

Open githelper.py in a text editor and look for this code:

```
# Add the arguments for using your specific server
parser.add_argument('--server', default="example.com", help='What server should I use?')
parser.add_argument('--user', default="tux", help='What user should I use?')
```

You can simple change `example.com` to your server and you change `tux` to your server and username. 

You can do the same thing with the port number. Personally, I don't use the standard port 22. If you're like me, you can change that also.
```
parser.add_argument('--port', '-p', default="22", help='Set the ssh port to something other than 22')
```

