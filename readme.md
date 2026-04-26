## About

A lot of us want to create our own private git repos without needing to rely on third-party tools like GitHub, GitLab, or even Gitea. If you're concerned about privacy, cloud-based tools always present issues because Terms of Service could change at any time, not to mention the fact that well-known services tend to be targets for hackers. Even self-hosting a service like Gitea or GitLab means that you need to worry about the proper care and updates of this software. Often, they have tons of services that you will never need.

Instead, what about just using git directly to create and clone repos without needing all of the overhead of these other systems? My scripts do that. They give you a way to quickly create a new repo on a remote machine or even on your local machine, clone the repo that you just created, and start working. These scripts are simple and each only does one job.

I hope they make your work a little easier if you want to go away from big hosted services.

## What’s included

- **CLI** (`cli/githelper.py`): manage bare repos locally or over SSH
- **GUI** (`gui/githelper-gui.py`, Tkinter):
  - **Remote Repos**: list/clone/create/rename/fork-copy/archive/delete on an SSH host
  - **Local Repos**: scan a “projects” folder that contains many different repos (GitHub/GitLab/private), view rich metadata, fetch/pull, open folder, launch `lazygit`
  - **Local Commit Heatmap**: a GitHub-style activity heatmap across your local repo collection

## Dependencies

### Required

- **Python 3**
- **git**
- **ssh** (for remote operations)

### GUI (Tkinter)

Tkinter ships with Python on most platforms. If your OS packages it separately, install the Tk bindings for Python (package names vary by distro).

### Optional

- **`lazygit`**: the Local Repos tab can open `lazygit` in a terminal for the selected repo  
  Install instructions: `https://github.com/jesseduffield/lazygit#installation`
- **`xterm`** (Linux/*BSD): used to launch `lazygit` in a terminal window

## Configuration

The GUI stores settings in `~/.githelperrc` (JSON). This includes:

- SSH server/user/port and remote repo directory
- the local base folder used for scanning repos and generating the heatmap

## How to use

### GUI

Run:

```bash
python3 gui/githelper-gui.py
```

Remote Repo workflow:

- Enter **Server/User/Port/Remote Directory**
- Click **List Repos**
- Select a repo and use **Clone/Create/Rename/Fork-Copy/Archive/Delete**

Local Repo workflow:

- Choose a **Base folder** containing your local repos (a single directory that contains many projects)
- Click **Scan Repos**
- Select a repo to view metadata + commit history
- Use **Fetch**, **Pull**, **Open Folder**, or **lazygit**

### CLI

`cli/githelper.py` allows you to use any SSH connection as a place to store git repositories. This can be on a Raspberry Pi in your own home or on a server in another country. As long as you have SSH access to that device, `cli/githelper.py` will be able to work with it.

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

## Tips

- **Rename**: renames the bare repo on the server. Your existing local clone will still point at the old URL until you update `origin` (or re-clone).
- **Fork/Copy**: copies an existing bare repo to a new name on the server. It does not retain any “relationship” like GitHub forks do.
- **Fast defaults**: if you don’t want to type flags in the CLI, `aliases.md` can hold shell aliases for your common server/user/dir/port values.
