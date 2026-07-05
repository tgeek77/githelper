"""Remote repository inspection over SSH."""

import shlex
from concurrent.futures import ThreadPoolExecutor

from githelper.ssh import remote_cd_cmd, repo_git_dirname, run_ssh, validate_ssh_inputs


def _meta_cmd(cd_cmd, repo_git):
    return (
        "set -e; "
        f"{cd_cmd}; "
        f"REPO={repo_git}; "
        'printf \'Repo: %s\\n\' "$REPO"; '
        "printf 'HEAD: '; "
        'git --git-dir "$REPO" symbolic-ref -q --short HEAD || echo \'(detached/unknown)\'; '
        "printf 'Last commit: '; "
        'git --git-dir "$REPO" log -1 --format=\'%h %ci %an %s\' 2>/dev/null || echo \'(no commits)\'; '
        "printf 'Branches: '; "
        'git --git-dir "$REPO" for-each-ref refs/heads --format=\'%(refname:short)\' | wc -l | tr -d \' \'; '
        "printf '\\nTags: '; "
        'git --git-dir "$REPO" tag -l | wc -l | tr -d \' \'; '
        "printf '\\nObject size: '; "
        'git --git-dir "$REPO" count-objects -vH | sed -n \'s/^size-pack: //p\'; '
        "printf '\\nLoose objects: '; "
        'git --git-dir "$REPO" count-objects -vH | sed -n \'s/^count: //p\'; '
        "printf '\\nPacked objects: '; "
        'git --git-dir "$REPO" count-objects -vH | sed -n \'s/^in-pack: //p\'; '
        "printf '\\n'"
    )


def _merges_cmd(cd_cmd, repo_git, limit=50):
    return (
        "set -e; "
        f"{cd_cmd}; "
        f"REPO={repo_git}; "
        f"git --git-dir \"$REPO\" log --merges --oneline --decorate -n {int(limit)} 2>/dev/null || true"
    )


def _commits_cmd(cd_cmd, repo_git, limit=100):
    return (
        "set -e; "
        f"{cd_cmd}; "
        f"REPO={repo_git}; "
        f"git --git-dir \"$REPO\" log --oneline --decorate -n {int(limit)} 2>/dev/null || true"
    )


def fetch_repo_info(
    server,
    user,
    port,
    ssh_dir,
    repo_name,
    include_merges=False,
    commits_limit=None,
    verbose=False,
):
    """
    Fetch remote repo metadata and optional merge/commit history.

    Returns dict with keys: metadata, merges, commits (merges/commits may be None).
    """
    validate_ssh_inputs(server, user, port, ssh_dir)
    repo_name = repo_name.strip().removesuffix(".git")
    cd_cmd = remote_cd_cmd(ssh_dir)
    repo_git = shlex.quote(repo_git_dirname(repo_name))

    meta_cmd = _meta_cmd(cd_cmd, repo_git)
    merges_cmd = _merges_cmd(cd_cmd, repo_git) if include_merges else None
    commits_cmd = _commits_cmd(cd_cmd, repo_git, commits_limit or 100) if commits_limit else None

    def ssh(cmd):
        return run_ssh(server, user, port, cmd, verbose=verbose).stdout

    with ThreadPoolExecutor(max_workers=3) as pool:
        meta_f = pool.submit(ssh, meta_cmd)
        merges_f = pool.submit(ssh, merges_cmd) if merges_cmd else None
        commits_f = pool.submit(ssh, commits_cmd) if commits_cmd else None
        meta = meta_f.result().strip()
        merges = merges_f.result().strip() if merges_f else None
        commits = commits_f.result().strip() if commits_f else None

    return {
        "repo": repo_name,
        "metadata": meta,
        "merges": merges,
        "commits": commits,
    }


def format_repo_info(info, include_merges=False, include_commits=False):
    """Format repo info dict as human-readable text."""
    parts = [info["metadata"]]
    if include_merges:
        merges = info.get("merges") or ""
        parts.append("\nMerge history:\n" + (merges if merges else "(No merge commits found)"))
    if include_commits:
        commits = info.get("commits") or ""
        parts.append("\nCommit history:\n" + (commits if commits else "(No commits found)"))
    return "\n".join(parts).strip() + "\n"
