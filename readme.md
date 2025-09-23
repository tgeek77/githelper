## About:

A lot of us want to create our own private git repos without needing to rely on third-party tools like GitHub, GitLab, or even Gitea. If you're concerned about privacy, cloud-based tools always present issues because Terms of Service could change at any time, not to mention the fact that well-known services tend to be targets for hackers. Even self-hosting a service like Gitea or GitLab means that you need to worry about the proper care and updates of this software. Often, they have tons of services that you will never need.

Instead, what about just using git directly to create and clone repos without needing all of the overhead of these other systems? My scripts do that. They give you a way to quickly create a new repo on a remote machine or even on your local machine, clone the repo that you just created, and start working. These scripts are simple and each only does one job.

I hope they make your work a little easier if you want to go away from big hosted services.

## How to Use githelper:

`githelper.py` allows you to use any SSH connection as a place to store git repositories. This can be on a Raspberry Pi in your own home or on a server in another country. As long as you have SSH access to that device, `githelper.py` will be able to work with it.

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
  --loc LOC             Use local directory, not ssh
```

### Note on Cloning:
The clone function can seem like it froze up if the repository that you are cloning is very large and your connection is slow.

## Updates:
- Added rename and fork functions.
  - **Rename** will rename the repository on the server; you will need to re-clone the repo or manually change the upstream repo URL in your local repo.
  - **Fork** will copy an existing repository on the server to a new name. You can then clone the fork to a new local repo. The original and the fork will have no relation, so if you decide to merge them again in the future, that will need to be done manually.

- `aliases.md` contains a few BASH aliases that you can use with githelper. I thought long and hard about writing a function into githelper that would cache your settings so you don't have to write them manually every time. I think wrapping a simple alias around the command is a better way to go.

There is one more option if you don't want to use aliases:

Open `githelper.py` in a text editor and look for this code:

```python
# Add the arguments for using your specific server
parser.add_argument('--server', default="example.com", help='What server should I use?')
parser.add_argument('--user', default="tux", help='What user should I use?')
```

You can simply change example.com to your server and tux to your username.

You can do the same thing with the port number. Personally, I don't use the standard port 22. If you're like me, you can change that also.

```
python
parser.add_argument('--port', '-p', default="22", help='Set the ssh port to something other than 22')
```