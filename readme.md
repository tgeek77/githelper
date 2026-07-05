## About

A lot of us want to create our own private git repos without needing to rely on third-party tools like GitHub, GitLab, or even Gitea. If you're concerned about privacy, cloud-based tools always present issues because Terms of Service could change at any time, not to mention the fact that well-known services tend to be targets for hackers. Even self-hosting a service like Gitea or GitLab means that you need to worry about the proper care and updates of this software. Often, they have tons of services that you will never need.

Instead, what about just using git directly to create and clone repos without needing all of the overhead of these other systems? My scripts do that. They give you a way to quickly create a new repo on a remote machine or even on your local machine, clone the repo that you just created, and start working. These scripts are simple and each only does one job.

I hope they make your work a little easier if you want to go away from big hosted services.

## What's included

- **CLI** (`cli/githelper.py`): manage bare repos locally or over SSH, inspect remote repos, and show a terminal commit heatmap
- **GUI** (`gui/githelper-gui.py`, Tkinter):
  - **Remote Repos**: list/clone/create/rename/fork-copy/archive/delete on an SSH host
  - **Local Repos**: scan a "projects" folder that contains many different repos (GitHub/GitLab/private), view rich metadata, fetch/pull, open folder
  - **Local Commit Heatmap**: a GitHub-style activity heatmap across your local repo collection

## Dependencies

### Required

- **Python 3**
- **git**
- **ssh** (for remote operations)

### GUI (Tkinter)

Tkinter ships with Python on most platforms. If your OS packages it separately, install the Tk bindings for Python (package names vary by distro).

## Configuration

Both the CLI and GUI use `~/.githelperrc` (JSON). The GUI writes this file when you change settings; the CLI reads it for defaults.

Keys:

- `server`, `user`, `port`, `dir` — SSH settings for remote bare-repo commands
- `local_repo_base` — folder used by `githelper heatmap` (and the GUI local/heatmap tabs)

Inspect config:

```bash
python3 cli/githelper.py config show
python3 cli/githelper.py config path
```

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
- Use **Fetch**, **Pull**, or **Open Folder**

### CLI

Run from the repo root:

```bash
python3 cli/githelper.py --help
```

Global flags (place **before** the subcommand):

- `--server`, `--user`, `--port`, `--dir` — remote SSH settings (defaults from `~/.githelperrc`)
- `--loc` — local bare-repo directory for `bare` commands (default: `/srv/git`)
- `--verbose` — print commands as they run
- `--json` — machine-readable output where supported

#### Remote bare repos (SSH)

```bash
# List repos on a remote host (uses ~/.githelperrc defaults when flags omitted)
python3 cli/githelper.py remote list --server example.com --dir ~/repos

# Create, clone, rename, copy, archive, delete
python3 cli/githelper.py remote create myproject --server example.com --dir ~/repos
python3 cli/githelper.py remote clone myproject --dest ~/src --server example.com
python3 cli/githelper.py remote rename old new --server example.com
python3 cli/githelper.py remote fork source copy --server example.com
python3 cli/githelper.py remote archive myproject --server example.com
python3 cli/githelper.py remote delete myproject --server example.com

# Inspect a remote repo (metadata; optional history)
python3 cli/githelper.py remote info myproject --server example.com
python3 cli/githelper.py remote info myproject --merges --commits 20 --server example.com
python3 cli/githelper.py remote info myproject --json --server example.com
```

Destructive commands prompt for confirmation unless you pass `-y`.

#### Local bare repos

For bare repos on this machine (no SSH):

```bash
python3 cli/githelper.py --loc /srv/git bare list
python3 cli/githelper.py --loc /srv/git bare create myproject
python3 cli/githelper.py --loc /srv/git bare clone myproject
python3 cli/githelper.py --loc /srv/git bare delete myproject -y
```

#### Commit heatmap

Aggregate commit activity across repos in a folder (one level deep):

```bash
python3 cli/githelper.py heatmap --base ~/projects
python3 cli/githelper.py heatmap --day 2026-03-15
python3 cli/githelper.py heatmap --json
```

Uses `local_repo_base` from `~/.githelperrc` when `--base` is omitted.

### Migration from old flag-style CLI

The previous flag-based interface still works but prints a deprecation notice. Prefer subcommands:

| Old | New |
|-----|-----|
| `-l` / `--list` | `remote list` or `bare list` |
| `-c REPO` / `--clone REPO` | `remote clone REPO` or `bare clone REPO` |
| `-n REPO` / `--new REPO` | `remote create REPO` or `bare create REPO` |
| `-a REPO` / `--archive REPO` | `remote archive REPO` or `bare archive REPO` |
| `--remove REPO` | `remote delete REPO` or `bare delete REPO` |
| `-rn --old-repo A --new-repo B` | `remote rename A B` or `bare rename A B` |
| `-f --old-repo A --new-repo B` | `remote fork A B` or `bare fork A B` |
| `--server HOST …` (remote) | same flags, before subcommand |
| `--loc PATH` (local bare) | `--loc PATH bare …` |

### Note on cloning

Clone shows progress directly from git (no captured output). Very large repos over slow links may still take a while.

## Linux AppImage releases

Pre-built **x86_64** AppImages are published on [GitHub Releases](https://github.com/tgeek77/githelper/releases):

- `githelper-cli-VERSION-x86_64.AppImage` — command-line tool
- `githelper-gui-VERSION-x86_64.AppImage` — desktop GUI

```bash
chmod +x githelper-cli-2.0.0-x86_64.AppImage
./githelper-cli-2.0.0-x86_64.AppImage remote list

chmod +x githelper-gui-2.0.0-x86_64.AppImage
./githelper-gui-2.0.0-x86_64.AppImage
```

**Requirements:** `git` and `openssh-client` must still be installed on your system and available on your `PATH`. The AppImages bundle Python and githelper itself, not git or ssh.

### Build AppImages locally

```bash
sudo apt-get install python3-tk wget xvfb   # Debian/Ubuntu
chmod +x packaging/appimage/build.sh
packaging/appimage/build.sh all             # or: cli | gui
ls dist/*.AppImage
```

Releases are built automatically when a version tag is pushed (for example `v2.0.0`). You can also trigger a manual build from the **Actions** tab in GitHub.

## Tips

- **Rename**: renames the bare repo on the server. Your existing local clone will still point at the old URL until you update `origin` (or re-clone).
- **Fork/Copy**: copies an existing bare repo to a new name on the server. It does not retain any "relationship" like GitHub forks do.
- **Fast defaults**: use `~/.githelperrc` or shell aliases — see `alias.md`.
