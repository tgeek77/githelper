#!/usr/bin/python3
"""
Manage Git bare repositories locally or remotely, with local commit heatmaps.
"""

import argparse
import json
import sys
from pathlib import Path

# Allow running as python3 cli/githelper.py without installation.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from githelper import bare, config, heatmap, info, remote
from githelper.config import CONFIG_PATH, load_config, resolve_local_base, resolve_remote_settings
from githelper.errors import GithelperError

DEPRECATION = (
    "Note: flag-based usage is deprecated; use subcommands "
    "(e.g. 'githelper remote list'). Run 'githelper --help' for details."
)

LEGACY_OPS = {
    "list": "list",
    "clone": "clone",
    "new": "create",
    "archive": "archive",
    "remove": "delete",
    "rename": "rename",
    "fork": "fork",
}


def confirm_delete(target, assume_yes=False):
    """Prompt before destructive delete unless -y was passed."""
    if assume_yes:
        return True
    try:
        answer = input(f"Delete {target} permanently? [y/N]: ").strip().lower()
    except EOFError:
        return False
    return answer in ("y", "yes")


def add_remote_parent(subparsers):
    """Add remote subcommand group."""
    remote_parser = subparsers.add_parser(
        "remote",
        help="Manage bare repos on a remote SSH host",
    )
    remote_sub = remote_parser.add_subparsers(dest="remote_cmd", required=True)

    for name, help_text in [
        ("list", "List bare repos on the remote host"),
        ("clone", "Clone a remote bare repo locally"),
        ("create", "Create a new bare repo on the remote host"),
        ("rename", "Rename a bare repo on the remote host"),
        ("fork", "Copy a bare repo to a new name on the remote host"),
        ("archive", "Archive a bare repo to a tarball on the remote host"),
        ("delete", "Delete a bare repo on the remote host"),
        ("info", "Show metadata and optional history for a remote repo"),
    ]:
        p = remote_sub.add_parser(name, help=help_text)
        if name in ("clone", "create", "archive", "delete", "info"):
            p.add_argument("repo", help="Repository name (without .git)")
        if name == "clone":
            p.add_argument("--dest", help="Destination directory (default: ./REPO)")
        if name == "rename":
            p.add_argument("old_name", help="Current repository name")
            p.add_argument("new_name", help="New repository name")
        if name == "fork":
            p.add_argument("old_name", help="Source repository name")
            p.add_argument("new_name", help="Destination repository name")
        if name == "info":
            p.add_argument("--merges", action="store_true", help="Include merge history")
            p.add_argument(
                "--commits",
                nargs="?",
                const=100,
                type=int,
                metavar="N",
                help="Include last N commits (default 100 when flag is used)",
            )
        if name == "delete":
            p.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")


def add_bare_parent(subparsers):
    """Add bare subcommand group for local bare repos."""
    bare_parser = subparsers.add_parser(
        "bare",
        help="Manage local bare repositories",
    )
    bare_sub = bare_parser.add_subparsers(dest="bare_cmd", required=True)

    for name, help_text in [
        ("list", "List local bare repos"),
        ("clone", "Clone a local bare repo to a working copy"),
        ("create", "Create a new local bare repo"),
        ("rename", "Rename a local bare repo"),
        ("fork", "Copy a local bare repo to a new name"),
        ("archive", "Archive a local bare repo to a tarball"),
        ("delete", "Delete a local bare repo"),
    ]:
        p = bare_sub.add_parser(name, help=help_text)
        if name in ("clone", "create", "archive", "delete"):
            p.add_argument("repo", help="Repository name (without .git)")
        if name == "clone":
            p.add_argument("--dest", help="Destination directory (default: ./REPO)")
        if name == "rename":
            p.add_argument("old_name", help="Current repository name")
            p.add_argument("new_name", help="New repository name")
        if name == "fork":
            p.add_argument("old_name", help="Source repository name")
            p.add_argument("new_name", help="Destination repository name")
        if name == "delete":
            p.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")


def build_parser():
    """Build the top-level argument parser."""
    cfg = load_config()
    remote_defaults = resolve_remote_settings(cfg)

    parser = argparse.ArgumentParser(
        description="Manage Git bare repositories locally or remotely via SSH",
    )
    parser.add_argument("--verbose", action="store_true", help="Show commands as they run")
    parser.add_argument(
        "--server",
        default=remote_defaults["server"] or None,
        help="SSH server hostname (remote commands; default from ~/.githelperrc)",
    )
    parser.add_argument(
        "--user",
        default=remote_defaults["user"],
        help="SSH username (default: git or ~/.githelperrc)",
    )
    parser.add_argument(
        "--port", "-p",
        default=remote_defaults["port"],
        help="SSH port (default: 22 or ~/.githelperrc)",
    )
    parser.add_argument(
        "--dir", "-d",
        default=remote_defaults["dir"],
        help="Remote bare-repo directory (default: /srv/git or ~/.githelperrc)",
    )
    parser.add_argument(
        "--loc",
        default="/srv/git",
        help="Local bare-repo directory for 'bare' commands (default: /srv/git)",
    )
    parser.add_argument("--json", action="store_true", help="JSON output where supported")

    subparsers = parser.add_subparsers(dest="command")

    add_remote_parent(subparsers)
    add_bare_parent(subparsers)

    heatmap_parser = subparsers.add_parser(
        "heatmap",
        help="Show a commit activity heatmap for local repos",
    )
    heatmap_parser.add_argument(
        "--base",
        help="Base folder containing repos (default: local_repo_base from ~/.githelperrc)",
    )
    heatmap_parser.add_argument(
        "--day",
        metavar="YYYY-MM-DD",
        help="Show per-repo commit breakdown for one day",
    )
    heatmap_parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colors in heatmap output",
    )

    config_parser = subparsers.add_parser("config", help="Show configuration")
    config_sub = config_parser.add_subparsers(dest="config_cmd", required=True)
    config_sub.add_parser("show", help="Show effective configuration defaults")
    config_sub.add_parser("path", help="Print config file path")

    _add_legacy_flags(parser)
    return parser


def _add_legacy_flags(parser):
    """Attach deprecated flat flags for backward compatibility."""
    group = parser.add_argument_group("deprecated flags (use subcommands instead)")
    group.add_argument("--list", "-l", action="store_true", help=argparse.SUPPRESS)
    group.add_argument("--clone", "-c", metavar="REPO", help=argparse.SUPPRESS)
    group.add_argument("--new", "-n", metavar="REPO", help=argparse.SUPPRESS)
    group.add_argument("--archive", "-a", metavar="REPO", help=argparse.SUPPRESS)
    group.add_argument("--remove", "--rm", dest="remove", metavar="REPO", help=argparse.SUPPRESS)
    group.add_argument("--rename", "-rn", action="store_true", help=argparse.SUPPRESS)
    group.add_argument("--fork", "-f", action="store_true", help=argparse.SUPPRESS)
    group.add_argument("--old-repo", help=argparse.SUPPRESS)
    group.add_argument("--new-repo", help=argparse.SUPPRESS)


def _remote_kwargs(args):
    return {
        "server": args.server,
        "user": args.user,
        "port": args.port,
        "ssh_dir": args.dir,
        "verbose": args.verbose,
    }


def _handle_remote(args):
    kw = _remote_kwargs(args)
    cmd = args.remote_cmd

    if cmd == "list":
        repos = remote.list_repos(**kw)
        if args.json:
            print(json.dumps(repos, indent=2))
        else:
            print("\n".join(repos))
        return

    if cmd == "clone":
        dest = remote.clone_repo(repo_name=args.repo, dest=args.dest, **kw)
        if not args.json:
            print(f"Cloned to {dest}")
        else:
            print(json.dumps({"repo": args.repo, "dest": dest}, indent=2))
        return

    if cmd == "create":
        remote.create_repo(repo_name=args.repo, **kw)
        print(f"Created {args.repo}.git")
        return

    if cmd == "rename":
        remote.rename_repo(old_name=args.old_name, new_name=args.new_name, **kw)
        print(f"Renamed {args.old_name} -> {args.new_name}")
        return

    if cmd == "fork":
        remote.fork_repo(old_name=args.old_name, new_name=args.new_name, **kw)
        print(f"Copied {args.old_name} -> {args.new_name}")
        return

    if cmd == "archive":
        remote.archive_repo(repo_name=args.repo, **kw)
        print(f"Archived {args.repo}.tgz on remote host ({args.dir})")
        return

    if cmd == "delete":
        target = f"remote repo '{args.repo}' on {args.server}:{args.dir}"
        if not confirm_delete(target, assume_yes=args.yes):
            print("Cancelled.")
            return
        remote.delete_repo(repo_name=args.repo, **kw)
        print(f"Deleted {args.repo}.git")
        return

    if cmd == "info":
        data = info.fetch_repo_info(
            repo_name=args.repo,
            include_merges=args.merges,
            commits_limit=args.commits,
            **kw,
        )
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            include_commits = args.commits is not None
            print(info.format_repo_info(data, args.merges, include_commits))


def _handle_bare(args):
    location = args.loc
    verbose = args.verbose

    if args.bare_cmd == "list":
        repos = bare.list_repos(location, verbose=verbose)
        if args.json:
            print(json.dumps(repos, indent=2))
        else:
            print("\n".join(repos))
        return

    if args.bare_cmd == "clone":
        dest = bare.clone_repo(location, args.repo, dest=args.dest, verbose=verbose)
        if args.json:
            print(json.dumps({"repo": args.repo, "dest": dest}, indent=2))
        else:
            print(f"Cloned to {dest}")
        return

    if args.bare_cmd == "create":
        bare.create_repo(location, args.repo, verbose=verbose)
        print(f"Created {args.repo}.git")
        return

    if args.bare_cmd == "rename":
        bare.rename_repo(location, args.old_name, args.new_name, verbose=verbose)
        print(f"Renamed {args.old_name} -> {args.new_name}")
        return

    if args.bare_cmd == "fork":
        bare.fork_repo(location, args.old_name, args.new_name, verbose=verbose)
        print(f"Copied {args.old_name} -> {args.new_name}")
        return

    if args.bare_cmd == "archive":
        bare.archive_repo(location, args.repo, verbose=verbose)
        print(f"Archived to {Path(location).expanduser() / (args.repo + '.tgz')}")
        return

    if args.bare_cmd == "delete":
        target = f"bare repo '{args.repo}' in {location}"
        if not confirm_delete(target, assume_yes=args.yes):
            print("Cancelled.")
            return
        bare.delete_repo(location, args.repo, verbose=verbose)
        print(f"Deleted {args.repo}.git")


def _handle_heatmap(args):
    cfg = load_config()
    base = resolve_local_base(cfg, args.base)
    if not base:
        raise GithelperError(
            "Base folder required. Pass --base or set local_repo_base in ~/.githelperrc"
        )

    commit_counter, day_details = heatmap.aggregate_commits(base)

    if args.day:
        print(heatmap.format_day_breakdown(day_details, args.day))
        return

    if args.json:
        print(heatmap.dumps_json(heatmap.export_json(commit_counter, day_details)))
        return

    print(heatmap.render_heatmap(commit_counter, use_color=not args.no_color))


def _handle_config(args):
    if args.config_cmd == "path":
        print(CONFIG_PATH)
        return

    cfg = load_config()
    remote_defaults = resolve_remote_settings(cfg)
    local_base = resolve_local_base(cfg)
    output = {
        "config_path": str(CONFIG_PATH),
        "remote": remote_defaults,
        "local_repo_base": local_base,
    }
    print(json.dumps(output, indent=2))


def _dispatch_legacy(args):
    """Map deprecated flags to subcommand handlers."""
    print(DEPRECATION, file=sys.stderr)

    legacy_op = None
    for flag, op in LEGACY_OPS.items():
        value = getattr(args, flag if flag != "remove" else "remove", None)
        if flag == "list" and args.list:
            legacy_op = op
            break
        if flag in ("rename", "fork") and value:
            legacy_op = op
            break
        if value and flag not in ("list", "rename", "fork"):
            legacy_op = op
            break

    if not legacy_op:
        return False

    remote_mode = bool(args.server)

    if legacy_op == "rename":
        if not args.old_repo or not args.new_repo:
            raise GithelperError("--rename requires both --old-repo and --new-repo")
        if remote_mode:
            remote.rename_repo(old_name=args.old_repo, new_name=args.new_repo, **_remote_kwargs(args))
        else:
            bare.rename_repo(args.loc, args.old_repo, args.new_repo, verbose=args.verbose)
        print(f"Renamed {args.old_repo} -> {args.new_repo}")
        return True

    if legacy_op == "fork":
        if not args.old_repo or not args.new_repo:
            raise GithelperError("--fork requires both --old-repo and --new-repo")
        if remote_mode:
            remote.fork_repo(old_name=args.old_repo, new_name=args.new_repo, **_remote_kwargs(args))
        else:
            bare.fork_repo(args.loc, args.old_repo, args.new_repo, verbose=args.verbose)
        print(f"Copied {args.old_repo} -> {args.new_repo}")
        return True

    repo = getattr(args, legacy_op if legacy_op != "create" else "new", None)
    if legacy_op == "list":
        if remote_mode:
            repos = remote.list_repos(**_remote_kwargs(args))
        else:
            repos = bare.list_repos(args.loc, verbose=args.verbose)
        print("\n".join(repos))
        return True

    if legacy_op == "clone":
        if remote_mode:
            dest = remote.clone_repo(repo_name=repo, **_remote_kwargs(args))
        else:
            dest = bare.clone_repo(args.loc, repo, verbose=args.verbose)
        print(f"Cloned to {dest}")
        return True

    if legacy_op == "create":
        if remote_mode:
            remote.create_repo(repo_name=repo, **_remote_kwargs(args))
        else:
            bare.create_repo(args.loc, repo, verbose=args.verbose)
        print(f"Created {repo}.git")
        return True

    if legacy_op == "archive":
        if remote_mode:
            remote.archive_repo(repo_name=repo, **_remote_kwargs(args))
        else:
            bare.archive_repo(args.loc, repo, verbose=args.verbose)
        print(f"Archived {repo}")
        return True

    if legacy_op == "delete":
        repo = args.remove
        if remote_mode:
            target = f"remote repo '{repo}' on {args.server}"
        else:
            target = f"bare repo '{repo}' in {args.loc}"
        if not confirm_delete(target, assume_yes=False):
            print("Cancelled.")
            return True
        if remote_mode:
            remote.delete_repo(repo_name=repo, **_remote_kwargs(args))
        else:
            bare.delete_repo(args.loc, repo, verbose=args.verbose)
        print(f"Deleted {repo}.git")
        return True

    return False


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "remote":
            _handle_remote(args)
        elif args.command == "bare":
            _handle_bare(args)
        elif args.command == "heatmap":
            _handle_heatmap(args)
        elif args.command == "config":
            _handle_config(args)
        elif _dispatch_legacy(args):
            pass
        else:
            parser.print_help()
    except GithelperError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(exc.returncode if exc.returncode else 1)


if __name__ == "__main__":
    main()
