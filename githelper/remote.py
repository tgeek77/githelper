"""Remote bare-repository operations over SSH."""

import shlex
from pathlib import Path

from githelper.errors import GithelperError
from githelper.ssh import (
    remote_cd_cmd,
    remote_path_for_git_url,
    repo_git_dirname,
    run_local,
    run_ssh,
    validate_ssh_inputs,
)


def _conn(server, user, port, ssh_dir):
    return validate_ssh_inputs(server, user, port, ssh_dir)


def _list_cmd(ssh_dir):
    cd_cmd = remote_cd_cmd(ssh_dir)
    return (
        "set -e; "
        f"{cd_cmd}; "
        "for d in *.git; do "
        '  [ -d "$d" ] || continue; '
        '  printf \'%s\\n\' "${d%.git}"; '
        "done"
    )


def list_repos(server, user, port, ssh_dir, verbose=False):
    """List bare repos on a remote host."""
    _conn(server, user, port, ssh_dir)
    result = run_ssh(server, user, port, _list_cmd(ssh_dir), verbose=verbose)
    repos = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return repos


def repo_exists(server, user, port, ssh_dir, repo_name, verbose=False):
    """Check whether a bare repo exists on the remote host."""
    _conn(server, user, port, ssh_dir)
    cd_cmd = remote_cd_cmd(ssh_dir)
    repo_git = shlex.quote(repo_git_dirname(repo_name))
    cmd = f"set -e; {cd_cmd}; [ -d {repo_git} ]"
    result = run_ssh(server, user, port, cmd, verbose=verbose, check=False)
    return result.returncode == 0


def require_repo(server, user, port, ssh_dir, repo_name, verbose=False):
    """Raise if repo does not exist on remote."""
    if not repo_exists(server, user, port, ssh_dir, repo_name, verbose=verbose):
        name = repo_git_dirname(repo_name)
        raise GithelperError(f"Remote repo '{name}' not found in {ssh_dir!r}.")


def create_repo(server, user, port, ssh_dir, repo_name, verbose=False):
    """Create a new bare repo on the remote host."""
    _conn(server, user, port, ssh_dir)
    repo_name = repo_name.strip().removesuffix(".git")
    cd_cmd = remote_cd_cmd(ssh_dir)
    repo_git = shlex.quote(repo_git_dirname(repo_name))
    cmd = f"set -e; {cd_cmd}; git init --bare --initial-branch=main {repo_git}"
    return run_ssh(server, user, port, cmd, verbose=verbose)


def clone_repo(server, user, port, ssh_dir, repo_name, dest=None, verbose=False):
    """Clone a remote bare repo to a local working copy."""
    _conn(server, user, port, ssh_dir)
    repo_name = repo_name.strip().removesuffix(".git")
    require_repo(server, user, port, ssh_dir, repo_name, verbose=verbose)
    url_path = remote_path_for_git_url(ssh_dir)
    url = f"ssh://{user}@{server}:{port}{url_path}/{repo_name}.git"
    if dest:
        dest_path = str(Path(dest).expanduser().resolve())
    else:
        dest_path = str(Path.cwd() / repo_name)
    cmd = ["git", "clone", url, dest_path]
    run_local(cmd, verbose=verbose, capture=False)
    return dest_path


def rename_repo(server, user, port, ssh_dir, old_name, new_name, verbose=False):
    """Rename a bare repo on the remote host."""
    _conn(server, user, port, ssh_dir)
    old_name = old_name.strip().removesuffix(".git")
    new_name = new_name.strip().removesuffix(".git")
    require_repo(server, user, port, ssh_dir, old_name, verbose=verbose)
    cd_cmd = remote_cd_cmd(ssh_dir)
    old_git = shlex.quote(repo_git_dirname(old_name))
    new_git = shlex.quote(repo_git_dirname(new_name))
    cmd = f"set -e; {cd_cmd}; mv -v {old_git} {new_git}"
    return run_ssh(server, user, port, cmd, verbose=verbose)


def fork_repo(server, user, port, ssh_dir, old_name, new_name, verbose=False):
    """Copy a bare repo to a new name on the remote host."""
    _conn(server, user, port, ssh_dir)
    old_name = old_name.strip().removesuffix(".git")
    new_name = new_name.strip().removesuffix(".git")
    require_repo(server, user, port, ssh_dir, old_name, verbose=verbose)
    cd_cmd = remote_cd_cmd(ssh_dir)
    old_git = shlex.quote(repo_git_dirname(old_name))
    new_git = shlex.quote(repo_git_dirname(new_name))
    cmd = f"set -e; {cd_cmd}; cp -R {old_git} {new_git}"
    return run_ssh(server, user, port, cmd, verbose=verbose)


def archive_repo(server, user, port, ssh_dir, repo_name, verbose=False):
    """Archive a bare repo to repo_name.tgz on the remote host."""
    _conn(server, user, port, ssh_dir)
    repo_name = repo_name.strip().removesuffix(".git")
    require_repo(server, user, port, ssh_dir, repo_name, verbose=verbose)
    cd_cmd = remote_cd_cmd(ssh_dir)
    repo_git = shlex.quote(repo_git_dirname(repo_name))
    out_name = shlex.quote(repo_name + ".tgz")
    cmd = f"set -e; {cd_cmd}; tar -czf {out_name} {repo_git}"
    return run_ssh(server, user, port, cmd, verbose=verbose)


def delete_repo(server, user, port, ssh_dir, repo_name, verbose=False):
    """Delete a bare repo on the remote host."""
    _conn(server, user, port, ssh_dir)
    repo_name = repo_name.strip().removesuffix(".git")
    require_repo(server, user, port, ssh_dir, repo_name, verbose=verbose)
    cd_cmd = remote_cd_cmd(ssh_dir)
    repo_git = shlex.quote(repo_git_dirname(repo_name))
    cmd = f"set -e; {cd_cmd}; rm -rf {repo_git}"
    return run_ssh(server, user, port, cmd, verbose=verbose)
