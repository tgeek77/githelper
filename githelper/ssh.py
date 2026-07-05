"""SSH helpers for remote bare-repo operations."""

import shlex
import subprocess

from githelper.errors import GithelperError, format_subprocess_error


def validate_ssh_inputs(server, user, port, ssh_dir):
    """Validate remote connection settings."""
    server = (server or "").strip()
    user = (user or "").strip()
    port = str(port or "").strip()
    ssh_dir = (ssh_dir or "").strip()

    if not server or not user or not ssh_dir:
        raise GithelperError("Server, user, and remote directory are required.")
    if not port.isdigit():
        raise GithelperError("Port must be a number.")
    return server, user, port, ssh_dir


def remote_cd_cmd(ssh_dir):
    """Build a safe remote cd command that expands ~ correctly."""
    ssh_dir = (ssh_dir or "").strip()
    if ssh_dir == "~":
        return 'cd -- "$HOME"'
    if ssh_dir.startswith("~/"):
        rest = ssh_dir[2:].rstrip("/")
        return 'cd -- "$HOME"/' + shlex.quote(rest)
    return f"cd -- {shlex.quote(ssh_dir.rstrip('/'))}"


def remote_path_for_git_url(ssh_dir):
    """
    Build an ssh:// URL path segment that works with home-relative dirs.
    Git's ssh URL supports /~/ to mean home directory.
    """
    ssh_dir = (ssh_dir or "").strip().rstrip("/")
    if ssh_dir == "~":
        return "/~"
    if ssh_dir.startswith("~/"):
        return "/~/" + ssh_dir[2:]
    if ssh_dir.startswith("/"):
        return ssh_dir
    return "/~/" + ssh_dir


def repo_git_dirname(repo_name_no_suffix):
    """Return bare repo directory name with .git suffix."""
    repo = (repo_name_no_suffix or "").strip().removesuffix(".git")
    return repo + ".git"


def run_ssh(server, user, port, command_text, verbose=False, check=True):
    """Run a shell command on a remote host via SSH."""
    cmd = ["ssh", "-p", str(port), f"{user}@{server}", command_text]
    if verbose:
        print(f"$ {' '.join(cmd)}")
        print(f"  remote: {command_text}")
    try:
        return subprocess.run(
            cmd,
            check=check,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise GithelperError(format_subprocess_error(exc), stderr=exc.stderr) from exc


def run_local(cmd, verbose=False, check=True, capture=True):
    """Run a local command."""
    if verbose:
        print(f"$ {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    kwargs = {"check": check, "text": True}
    if capture:
        kwargs["capture_output"] = True
    try:
        if isinstance(cmd, str):
            return subprocess.run(cmd, shell=True, **kwargs)
        return subprocess.run(cmd, **kwargs)
    except subprocess.CalledProcessError as exc:
        raise GithelperError(format_subprocess_error(exc), stderr=exc.stderr) from exc
