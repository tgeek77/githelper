"""Local bare-repository operations."""

import shlex
from pathlib import Path

from githelper.errors import GithelperError
from githelper.ssh import repo_git_dirname, run_local


def _location_path(location):
    return Path(location).expanduser().resolve()


def _repo_path(location, repo_name):
    loc = _location_path(location)
    return loc / repo_git_dirname(repo_name)


def repo_exists(location, repo_name):
    """Check whether a bare repo exists locally."""
    return _repo_path(location, repo_name).is_dir()


def require_repo(location, repo_name):
    """Raise if bare repo does not exist locally."""
    path = _repo_path(location, repo_name)
    if not path.is_dir():
        raise GithelperError(f"Bare repo '{path.name}' not found in {path.parent}.")


def list_repos(location, verbose=False):
    """List bare repos in a local directory."""
    loc = _location_path(location)
    if not loc.is_dir():
        raise GithelperError(f"Directory not found: {loc}")
    repos = sorted(
        p.name.removesuffix(".git")
        for p in loc.iterdir()
        if p.is_dir() and p.name.endswith(".git")
    )
    if verbose:
        print(f"$ ls {loc}/*.git")
    return repos


def create_repo(location, repo_name, verbose=False):
    """Create a new local bare repo."""
    repo_name = repo_name.strip().removesuffix(".git")
    path = _repo_path(location, repo_name)
    cmd = ["git", "init", "--bare", str(path)]
    return run_local(cmd, verbose=verbose)


def clone_repo(location, repo_name, dest=None, verbose=False):
    """Clone a local bare repo to a working copy."""
    repo_name = repo_name.strip().removesuffix(".git")
    require_repo(location, repo_name)
    loc = _location_path(location)
    url = f"file:///{loc / repo_git_dirname(repo_name)}"
    if dest:
        dest_path = str(Path(dest).expanduser().resolve())
    else:
        dest_path = str(Path.cwd() / repo_name)
    cmd = ["git", "clone", url, dest_path]
    run_local(cmd, verbose=verbose, capture=False)
    return dest_path


def rename_repo(location, old_name, new_name, verbose=False):
    """Rename a local bare repo."""
    old_name = old_name.strip().removesuffix(".git")
    new_name = new_name.strip().removesuffix(".git")
    require_repo(location, old_name)
    old_path = _repo_path(location, old_name)
    new_path = _repo_path(location, new_name)
    cmd = ["mv", "-v", str(old_path), str(new_path)]
    return run_local(cmd, verbose=verbose)


def fork_repo(location, old_name, new_name, verbose=False):
    """Copy a local bare repo to a new name."""
    old_name = old_name.strip().removesuffix(".git")
    new_name = new_name.strip().removesuffix(".git")
    require_repo(location, old_name)
    old_path = _repo_path(location, old_name)
    new_path = _repo_path(location, new_name)
    cmd = ["cp", "-rv", str(old_path), str(new_path)]
    return run_local(cmd, verbose=verbose)


def archive_repo(location, repo_name, verbose=False):
    """Archive a local bare repo to repo_name.tgz in the repo directory."""
    repo_name = repo_name.strip().removesuffix(".git")
    require_repo(location, repo_name)
    loc = _location_path(location)
    repo_path = loc / repo_git_dirname(repo_name)
    archive_path = loc / f"{repo_name}.tgz"
    cmd = ["tar", "-czf", str(archive_path), str(repo_path)]
    return run_local(cmd, verbose=verbose)


def delete_repo(location, repo_name, verbose=False):
    """Delete a local bare repo."""
    repo_name = repo_name.strip().removesuffix(".git")
    require_repo(location, repo_name)
    path = _repo_path(location, repo_name)
    cmd = f"rm -rfv {shlex.quote(str(path))}"
    return run_local(cmd, verbose=verbose)
