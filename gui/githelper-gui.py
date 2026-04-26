import subprocess
import os
import json
import collections
import threading
import shlex
import sys
import shutil
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
import tkinter as tk
from tkinter import (
    ttk, messagebox, filedialog, simpledialog
)


CONFIG_PATH = Path.home() / ".githelperrc"


class GithelperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Githelper - Easy Self Hosted Repos")
        self.root.geometry("1080x450")

        self.config = self.load_config()
        self._task_running = False

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Main tab
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Remote Repos")

        # Local repos tab
        self.local_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.local_frame, text="Local Repos")

        # Heatmap tab
        self.heatmap_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.heatmap_frame, text="Local Commit Heatmap")

        self.create_main_tab()
        self.create_local_tab()
        self.create_heatmap_tab()

    # == Config Management ==
    def load_config(self):
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as cfg:
                    return json.load(cfg)
            except Exception:
                pass
        return {}

    def save_config(self):
        self.config["server"] = self.server_var.get().strip()
        self.config["user"] = self.user_var.get().strip()
        self.config["port"] = self.port_var.get().strip()
        self.config["dir"] = self.dir_var.get().strip()
        self.config["local_repo_base"] = self.repo_base or ""
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            messagebox.showwarning("Warning", f"Failed to save config: {e}")

    # == UI Helpers ==
    def _set_status(self, text):
        self.status_var.set(text)

    def _append_log(self, text):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, text.rstrip() + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _validate_ssh_inputs(self):
        server = self.server_var.get().strip()
        user = self.user_var.get().strip()
        port = self.port_var.get().strip()
        ssh_dir = self.dir_var.get().strip()

        if not server or not user or not ssh_dir:
            raise ValueError("Server, User, and Remote Directory are required.")
        if not port.isdigit():
            raise ValueError("Port must be a number.")
        return server, user, port, ssh_dir

    def _run_in_background(self, label, work_fn, done_fn=None):
        if self._task_running:
            messagebox.showinfo("Busy", "Another operation is running. Please wait.")
            return

        self._task_running = True
        self._set_status(f"{label}…")
        self._append_log(f"[{label}] started")

        def runner():
            try:
                result = work_fn()
                error = None
            except Exception as e:
                result = None
                error = e

            def finish():
                self._task_running = False
                if error is not None:
                    err_text = str(error)
                    if isinstance(error, subprocess.CalledProcessError):
                        stderr = (error.stderr or "").strip()
                        if stderr:
                            err_text = f"{err_text}\n\n--- stderr ---\n{stderr}"
                    self._set_status(f"{label} failed")
                    self._append_log(f"[{label}] ERROR: {err_text}")
                    messagebox.showerror("Error", f"{label} failed:\n{err_text}")
                    return

                self._set_status(f"{label} done")
                self._append_log(f"[{label}] done")
                if done_fn is not None:
                    done_fn(result)

            self.root.after(0, finish)

        t = threading.Thread(target=runner, daemon=True)
        t.start()

    # == Main Tab UI ==
    def create_main_tab(self):
        # SSH Settings Group
        ssh_frame = ttk.LabelFrame(self.main_frame, text="SSH Settings")
        ssh_frame.pack(fill=tk.X, padx=10, pady=10)

        # Server/User/Port row
        top_row = ttk.Frame(ssh_frame)
        top_row.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(top_row, text="Server:").pack(side=tk.LEFT)
        self.server_var = tk.StringVar(
            value=self.config.get("server", "example.com")
        )
        ttk.Entry(top_row, textvariable=self.server_var, width=15).pack(
            side=tk.LEFT, padx=(0, 10)
        )

        ttk.Label(top_row, text="User:").pack(side=tk.LEFT)
        self.user_var = tk.StringVar(value=self.config.get("user", "tux"))
        ttk.Entry(top_row, textvariable=self.user_var, width=10).pack(
            side=tk.LEFT, padx=(0, 10)
        )

        ttk.Label(top_row, text="Port:").pack(side=tk.LEFT)
        self.port_var = tk.StringVar(value=self.config.get("port", "22"))
        ttk.Entry(top_row, textvariable=self.port_var, width=5).pack(
            side=tk.LEFT
        )

        # Directory row
        dir_row = ttk.Frame(ssh_frame)
        dir_row.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(dir_row, text="Remote Directory:").pack(side=tk.LEFT)
        self.dir_var = tk.StringVar(
            value=self.config.get("dir", "~/repos")
        )
        ttk.Entry(dir_row, textvariable=self.dir_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10)
        )

        # Buttons row
        button_row = ttk.Frame(ssh_frame)
        button_row.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            button_row, text="List Repos", command=self.list_repos
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            button_row, text="Clone", command=self.clone_repo
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            button_row, text="Create Repo", command=self.create_repo
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            button_row, text="Rename", command=self.rename_repo
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            button_row, text="Fork/Copy", command=self.fork_repo
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            button_row, text="Archive", command=self.archive_repo
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            button_row, text="Delete Repo", command=self.delete_repo
        ).pack(side=tk.LEFT)

        # Repositories list
        repo_frame = ttk.LabelFrame(self.main_frame, text="Repositories")
        repo_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        paned = ttk.Panedwindow(repo_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: repo list
        list_container = ttk.Frame(paned)
        paned.add(list_container, weight=1)

        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.repo_listbox = tk.Listbox(list_container, yscrollcommand=scrollbar.set)
        self.repo_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.repo_listbox.yview)

        # Right: details
        details_container = ttk.Frame(paned)
        paned.add(details_container, weight=2)

        details_header = ttk.Frame(details_container)
        details_header.pack(fill=tk.X)
        ttk.Label(details_header, text="Selected repo details").pack(side=tk.LEFT)
        ttk.Button(details_header, text="Refresh Details", command=self.refresh_repo_details).pack(side=tk.RIGHT)

        self.details_notebook = ttk.Notebook(details_container)
        self.details_notebook.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        meta_tab = ttk.Frame(self.details_notebook)
        merges_tab = ttk.Frame(self.details_notebook)
        commits_tab = ttk.Frame(self.details_notebook)
        self.details_notebook.add(meta_tab, text="Metadata")
        self.details_notebook.add(merges_tab, text="Merge History")
        self.details_notebook.add(commits_tab, text="Commit History")

        self.meta_text = tk.Text(meta_tab, wrap=tk.WORD, state=tk.DISABLED, height=10)
        meta_scroll = ttk.Scrollbar(meta_tab, orient=tk.VERTICAL, command=self.meta_text.yview)
        self.meta_text.configure(yscrollcommand=meta_scroll.set)
        meta_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.meta_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.merges_text = tk.Text(merges_tab, wrap=tk.NONE, state=tk.DISABLED, height=10)
        merges_v = ttk.Scrollbar(merges_tab, orient=tk.VERTICAL, command=self.merges_text.yview)
        merges_h = ttk.Scrollbar(merges_tab, orient=tk.HORIZONTAL, command=self.merges_text.xview)
        self.merges_text.configure(yscrollcommand=merges_v.set, xscrollcommand=merges_h.set)
        merges_v.pack(side=tk.RIGHT, fill=tk.Y)
        merges_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.merges_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.commits_text = tk.Text(commits_tab, wrap=tk.NONE, state=tk.DISABLED, height=10)
        commits_v = ttk.Scrollbar(commits_tab, orient=tk.VERTICAL, command=self.commits_text.yview)
        commits_h = ttk.Scrollbar(commits_tab, orient=tk.HORIZONTAL, command=self.commits_text.xview)
        self.commits_text.configure(yscrollcommand=commits_v.set, xscrollcommand=commits_h.set)
        commits_v.pack(side=tk.RIGHT, fill=tk.Y)
        commits_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.commits_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Auto-load details when selection changes
        self.repo_listbox.bind("<<ListboxSelect>>", lambda _e: self.refresh_repo_details())

        # Log + status
        bottom = ttk.Frame(self.main_frame)
        bottom.pack(fill=tk.BOTH, padx=10, pady=(0, 10))

        status_row = ttk.Frame(bottom)
        status_row.pack(fill=tk.X)
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_row, textvariable=self.status_var).pack(side=tk.LEFT)

        log_frame = ttk.LabelFrame(bottom, text="Log")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 0))
        log_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text = tk.Text(log_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        log_scroll.config(command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)

    def _set_text(self, widget, text):
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, text)
        widget.config(state=tk.DISABLED)

    def _classify_remote(self, url):
        u = (url or "").strip().lower()
        if "github.com" in u:
            return "GitHub"
        if "gitlab.com" in u:
            return "GitLab"
        if "bitbucket.org" in u:
            return "Bitbucket"
        if u.startswith("file://") or u.startswith("/"):
            return "Local"
        return "Other"

    def _run_git_local(self, repo, args, check=False):
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            check=check,
            capture_output=True,
            text=True,
        )

    def refresh_repo_details(self):
        selection = self.repo_listbox.curselection()
        if not selection:
            self._set_text(self.meta_text, "Select a repository to view metadata.")
            self._set_text(self.merges_text, "Select a repository to view merge history.")
            self._set_text(self.commits_text, "Select a repository to view commit history.")
            return

        repo_name = self.repo_listbox.get(selection[0]).strip().removesuffix(".git")
        self.save_config()

        def work():
            _server, _user, _port, ssh_dir = self._validate_ssh_inputs()
            cd_cmd = self._remote_cd_cmd(ssh_dir)
            repo_git = shlex.quote(self._repo_git_dirname(repo_name))

            meta_cmd = (
                "set -e; "
                f"{cd_cmd}; "
                f"REPO={repo_git}; "
                "printf 'Repo: %s\\n' \"$REPO\"; "
                "printf 'HEAD: '; "
                "git --git-dir \"$REPO\" symbolic-ref -q --short HEAD || echo '(detached/unknown)'; "
                "printf 'Last commit: '; "
                "git --git-dir \"$REPO\" log -1 --format='%h %ci %an %s' 2>/dev/null || echo '(no commits)'; "
                "printf 'Branches: '; "
                "git --git-dir \"$REPO\" for-each-ref refs/heads --format='%(refname:short)' | wc -l | tr -d ' '; "
                "printf '\\nTags: '; "
                "git --git-dir \"$REPO\" tag -l | wc -l | tr -d ' '; "
                "printf '\\nObject size: '; "
                "git --git-dir \"$REPO\" count-objects -vH | sed -n 's/^size-pack: //p'; "
                "printf '\\nLoose objects: '; "
                "git --git-dir \"$REPO\" count-objects -vH | sed -n 's/^count: //p'; "
                "printf '\\nPacked objects: '; "
                "git --git-dir \"$REPO\" count-objects -vH | sed -n 's/^in-pack: //p'; "
                "printf '\\n'"
            )

            merges_cmd = (
                "set -e; "
                f"{cd_cmd}; "
                f"REPO={repo_git}; "
                "git --git-dir \"$REPO\" log --merges --oneline --decorate -n 50 2>/dev/null || true"
            )

            commits_cmd = (
                "set -e; "
                f"{cd_cmd}; "
                f"REPO={repo_git}; "
                "git --git-dir \"$REPO\" log --oneline --decorate -n 100 2>/dev/null || true"
            )

            meta = self._run_ssh_command(meta_cmd).stdout
            merges = self._run_ssh_command(merges_cmd).stdout
            commits = self._run_ssh_command(commits_cmd).stdout
            return meta, merges, commits

        def done(result):
            meta, merges, commits = result
            self._set_text(self.meta_text, meta.strip() + "\n")
            self._set_text(self.merges_text, (merges.strip() + "\n") if merges.strip() else "(No merge commits found)\n")
            self._set_text(self.commits_text, (commits.strip() + "\n") if commits.strip() else "(No commits found)\n")

        self._run_in_background(f"Load details for {repo_name}", work, done)

    # == Heatmap Tab UI ==
    def create_local_tab(self):
        top = ttk.LabelFrame(self.local_frame, text="Local Repository Collection")
        top.pack(fill=tk.X, padx=10, pady=10)

        row = ttk.Frame(top)
        row.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(row, text="Base folder:").pack(side=tk.LEFT)
        self.local_base_var = tk.StringVar(value=self.config.get("local_repo_base", ""))
        ttk.Entry(row, textvariable=self.local_base_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 6))
        ttk.Button(row, text="Choose…", command=self.choose_local_base).pack(side=tk.LEFT)

        btns = ttk.Frame(top)
        btns.pack(fill=tk.X, padx=5, pady=(0, 5))
        ttk.Button(btns, text="Scan Repos", command=self.scan_local_repos).pack(side=tk.LEFT)
        ttk.Button(btns, text="Open Folder", command=self.open_selected_local_repo).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(btns, text="lazygit", command=self.lazygit_selected_local_repo).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(btns, text="Fetch", command=self.fetch_selected_local_repo).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(btns, text="Pull", command=self.pull_selected_local_repo).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(btns, text="Refresh Details", command=self.refresh_local_repo_details).pack(side=tk.RIGHT)

        body = ttk.Frame(self.local_frame)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        paned = ttk.Panedwindow(body, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left: list
        left = ttk.LabelFrame(paned, text="Repositories")
        paned.add(left, weight=1)

        lscroll = ttk.Scrollbar(left, orient=tk.VERTICAL)
        lscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.local_listbox = tk.Listbox(left, yscrollcommand=lscroll.set)
        self.local_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        lscroll.config(command=self.local_listbox.yview)

        # Right: details
        right = ttk.LabelFrame(paned, text="Details")
        paned.add(right, weight=2)

        self.local_details_notebook = ttk.Notebook(right)
        self.local_details_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        overview_tab = ttk.Frame(self.local_details_notebook)
        commits_tab = ttk.Frame(self.local_details_notebook)
        self.local_details_notebook.add(overview_tab, text="Overview")
        self.local_details_notebook.add(commits_tab, text="Commits")

        self.local_overview_text = tk.Text(overview_tab, wrap=tk.WORD, state=tk.DISABLED, height=12)
        ov_scroll = ttk.Scrollbar(overview_tab, orient=tk.VERTICAL, command=self.local_overview_text.yview)
        self.local_overview_text.configure(yscrollcommand=ov_scroll.set)
        ov_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.local_overview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.local_commits_text = tk.Text(commits_tab, wrap=tk.NONE, state=tk.DISABLED, height=12)
        c_v = ttk.Scrollbar(commits_tab, orient=tk.VERTICAL, command=self.local_commits_text.yview)
        c_h = ttk.Scrollbar(commits_tab, orient=tk.HORIZONTAL, command=self.local_commits_text.xview)
        self.local_commits_text.configure(yscrollcommand=c_v.set, xscrollcommand=c_h.set)
        c_v.pack(side=tk.RIGHT, fill=tk.Y)
        c_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.local_commits_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.local_listbox.bind("<<ListboxSelect>>", lambda _e: self.refresh_local_repo_details())

        self._set_text(self.local_overview_text, "Choose a base folder, scan repos, then select one.")
        self._set_text(self.local_commits_text, "Choose a repo to see commit history.")

    def choose_local_base(self):
        directory = filedialog.askdirectory(title="Select Base Folder Containing Repos")
        if directory:
            self.local_base_var.set(directory)
            self.repo_base = directory  # keep heatmap in sync with local collection
            self.save_config()

    def _selected_local_repo_path(self):
        sel = self.local_listbox.curselection()
        if not sel:
            return None
        return self.local_listbox.get(sel[0])

    def scan_local_repos(self):
        base = (self.local_base_var.get() or "").strip()
        if not base:
            messagebox.showwarning("Path Required", "Please choose a base folder first.")
            return
        base_path = Path(os.path.expanduser(base))
        if not base_path.is_dir():
            messagebox.showwarning("Invalid Path", "Base folder is not a directory.")
            return

        self.repo_base = str(base_path)  # keep heatmap in sync
        self.save_config()

        def work():
            repos = []
            # One-level deep scan by default (fast, matches common layouts).
            # Includes base itself if it is a repo.
            candidates = [base_path] + [p for p in base_path.iterdir() if p.is_dir()]
            for p in candidates:
                if (p / ".git").exists() and (p / ".git").is_dir():
                    repos.append(str(p))
            repos.sort(key=lambda s: s.lower())
            return repos

        def done(repos):
            self.local_listbox.delete(0, tk.END)
            for r in repos:
                self.local_listbox.insert(tk.END, r)
            self._set_status(f"Found {len(repos)} local repos")

        self._run_in_background("Scan local repos", work, done)

    def refresh_local_repo_details(self):
        repo_path = self._selected_local_repo_path()
        if not repo_path:
            self._set_text(self.local_overview_text, "Select a repository to view details.")
            self._set_text(self.local_commits_text, "Select a repository to view commit history.")
            return

        repo = Path(repo_path)

        def work():
            # Resolve git dir for worktrees/submodules
            git_dir_p = self._run_git_local(repo, ["rev-parse", "--git-dir"], check=False)
            git_dir = git_dir_p.stdout.strip()
            git_dir_abs = str((repo / git_dir).resolve()) if git_dir and not os.path.isabs(git_dir) else git_dir

            status_p = self._run_git_local(repo, ["status", "-sb"], check=False)
            porcelain_p = self._run_git_local(repo, ["status", "--porcelain=v1"], check=False)

            # Branch name: unborn repos don't have HEAD yet.
            branch_p = self._run_git_local(repo, ["symbolic-ref", "-q", "--short", "HEAD"], check=False)
            branch = branch_p.stdout.strip() if branch_p.returncode == 0 and branch_p.stdout.strip() else "(unborn/detached)"

            # Upstream and ahead/behind
            upstream_p = self._run_git_local(repo, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], check=False)
            upstream = upstream_p.stdout.strip() if upstream_p.returncode == 0 else ""
            ahead_behind = ""
            if upstream:
                ab_p = self._run_git_local(repo, ["rev-list", "--left-right", "--count", f"HEAD...{upstream}"], check=False)
                if ab_p.returncode == 0 and ab_p.stdout.strip():
                    left, right = (ab_p.stdout.strip().split() + ["0", "0"])[:2]
                    ahead_behind = f"ahead {right}, behind {left}"

            last_p = self._run_git_local(repo, ["log", "-1", "--format=%h %ci %an %s"], check=False)

            remotes_p = self._run_git_local(repo, ["remote", "-v"], check=False)
            origin_url_p = self._run_git_local(repo, ["remote", "get-url", "origin"], check=False)
            origin_url = origin_url_p.stdout.strip() if origin_url_p.returncode == 0 else ""
            origin_kind = self._classify_remote(origin_url) if origin_url else ""

            branches_count_p = self._run_git_local(repo, ["for-each-ref", "refs/heads", "--format=%(refname:short)"], check=False)
            branches_count = len([ln for ln in branches_count_p.stdout.splitlines() if ln.strip()]) if branches_count_p.stdout else 0

            tags_count_p = self._run_git_local(repo, ["tag", "-l"], check=False)
            tags_count = len([ln for ln in tags_count_p.stdout.splitlines() if ln.strip()]) if tags_count_p.stdout else 0

            stash_p = self._run_git_local(repo, ["stash", "list"], check=False)
            stash_count = len([ln for ln in stash_p.stdout.splitlines() if ln.strip()]) if stash_p.stdout else 0

            obj_p = self._run_git_local(repo, ["count-objects", "-vH"], check=False)
            obj_stats = obj_p.stdout.strip()

            # Dirty counts
            modified = untracked = added = deleted = renamed = conflicted = 0
            for line in porcelain_p.stdout.splitlines():
                if not line:
                    continue
                code = line[:2]
                if code == "??":
                    untracked += 1
                    continue
                x, y = code[0], code[1]
                if "U" in code:
                    conflicted += 1
                if x == "A" or y == "A":
                    added += 1
                if x == "D" or y == "D":
                    deleted += 1
                if x == "R" or y == "R":
                    renamed += 1
                if x == "M" or y == "M":
                    modified += 1

            # Timestamps: best-effort
            fetch_head = ""
            if git_dir_abs:
                try:
                    fh = Path(git_dir_abs) / "FETCH_HEAD"
                    if fh.exists():
                        ts = datetime.fromtimestamp(fh.stat().st_mtime)
                        fetch_head = ts.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    fetch_head = ""

            commits_p = self._run_git_local(repo, ["log", "--oneline", "--decorate", "-n", "100"], check=False)
            commits = commits_p.stdout

            status = status_p.stdout.strip() if status_p.stdout else (status_p.stderr or "").strip()
            remotes = remotes_p.stdout.strip()
            last = last_p.stdout.strip()

            overview_lines = [
                f"Path: {repo}",
                f"Git dir: {git_dir_abs or '(unknown)'}",
                f"Branch: {branch}",
            ]
            if upstream:
                overview_lines.append(f"Upstream: {upstream}" + (f" ({ahead_behind})" if ahead_behind else ""))
            else:
                overview_lines.append("Upstream: (none)")
            overview_lines.append(f"Last commit: {last or '(no commits)'}")
            if fetch_head:
                overview_lines.append(f"Last fetch: {fetch_head}")
            overview_lines.append("")
            overview_lines.append("Working tree:")
            overview_lines.append(f"- modified: {modified}, added: {added}, deleted: {deleted}, renamed: {renamed}, untracked: {untracked}, conflicts: {conflicted}")
            overview_lines.append(f"- stashes: {stash_count}")
            overview_lines.append("")
            overview_lines.append(f"Branches: {branches_count} | Tags: {tags_count}")
            if origin_url:
                overview_lines.append(f"Origin: {origin_kind} ({origin_url})")
            overview_lines.append("")
            overview_lines.append(status)
            overview_lines.append("")
            overview_lines.append("Remotes:")
            overview_lines.append(remotes if remotes else "(none)")
            overview_lines.append("")
            overview_lines.append("Object stats:")
            overview_lines.append(obj_stats if obj_stats else "(unavailable)")
            overview = "\n".join(overview_lines).strip() + "\n"

            return overview, commits

        def done(result):
            overview, commits = result
            self._set_text(self.local_overview_text, overview.strip() + "\n")
            self._set_text(self.local_commits_text, (commits.strip() + "\n") if commits.strip() else "(No commits found)\n")

        self._run_in_background(f"Load local details", work, done)

    def _open_path_in_file_manager(self, path):
        # Cross-platform-ish without extra deps
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
            return
        if sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
            return
        subprocess.run(["xdg-open", path], check=False)

    def _open_terminal_here(self, cwd, command):
        """
        Open a terminal window at cwd and run command.
        macOS: Terminal.app
        Linux/*BSD: xterm
        """
        cwd = str(Path(cwd).resolve())
        cd = f"cd {shlex.quote(cwd)}"
        cmd = f"{cd} && {command}"

        if sys.platform == "darwin":
            script = f'''
tell application "Terminal"
    activate
    do script {json.dumps(cmd)}
end tell
'''
            subprocess.run(["osascript", "-e", script], check=False)
            return

        if shutil.which("xterm"):
            subprocess.run(["xterm", "-e", "sh", "-lc", cmd], check=False)
            return

        raise RuntimeError("xterm not found on PATH. Please install xterm to use this feature.")

    def open_selected_local_repo(self):
        repo_path = self._selected_local_repo_path()
        if not repo_path:
            messagebox.showwarning("No Selection", "Please select a local repo first.")
            return
        self._open_path_in_file_manager(repo_path)

    def lazygit_selected_local_repo(self):
        repo_path = self._selected_local_repo_path()
        if not repo_path:
            messagebox.showwarning("No Selection", "Please select a local repo first.")
            return

        if not shutil.which("lazygit"):
            url = "https://github.com/jesseduffield/lazygit#installation"
            messagebox.showinfo(
                "lazygit not found",
                "Sorry — lazygit is not installed or not on your PATH.\n\n"
                f"Install instructions:\n{url}"
            )
            try:
                webbrowser.open(url)
            except Exception:
                pass
            return

        try:
            self._open_terminal_here(repo_path, "lazygit")
        except Exception as e:
            messagebox.showerror("Failed to open lazygit", str(e))

    def fetch_selected_local_repo(self):
        repo_path = self._selected_local_repo_path()
        if not repo_path:
            messagebox.showwarning("No Selection", "Please select a local repo first.")
            return
        repo = Path(repo_path)

        def work():
            return subprocess.run(
                ["git", "-C", str(repo), "fetch", "--all", "--prune"],
                check=True, capture_output=True, text=True
            )

        def done(_):
            self.refresh_local_repo_details()

        self._run_in_background("Fetch", work, done)

    def pull_selected_local_repo(self):
        repo_path = self._selected_local_repo_path()
        if not repo_path:
            messagebox.showwarning("No Selection", "Please select a local repo first.")
            return
        repo = Path(repo_path)

        def work():
            return subprocess.run(
                ["git", "-C", str(repo), "pull"],
                check=True, capture_output=True, text=True
            )

        def done(_):
            self.refresh_local_repo_details()

        self._run_in_background("Pull", work, done)

    def create_heatmap_tab(self):
        # Controls
        control_frame = ttk.Frame(self.heatmap_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        self.path_label = ttk.Label(
            control_frame, text="Repo path: (None selected)"
        )
        self.path_label.pack(side=tk.LEFT)

        ttk.Button(
            control_frame, text="Choose Folder", command=self.choose_path
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            control_frame, text="Generate Heatmap",
            command=self.generate_heatmap
        ).pack(side=tk.LEFT, padx=5)

        # Heatmap display
        heatmap_container = ttk.Frame(self.heatmap_frame)
        heatmap_container.pack(fill=tk.BOTH, expand=True, padx=10,
                               pady=(0, 10))

        # Canvas for heatmap
        self.canvas = tk.Canvas(heatmap_container, bg="white")
        v_scroll = ttk.Scrollbar(heatmap_container, orient=tk.VERTICAL,
                                 command=self.canvas.yview)
        h_scroll = ttk.Scrollbar(heatmap_container, orient=tk.HORIZONTAL,
                                 command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scroll.set,
                              xscrollcommand=h_scroll.set)

        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Legend
        legend_frame = ttk.Frame(self.heatmap_frame)
        legend_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Label(legend_frame, text="Fewer commits:").pack(side=tk.LEFT)
        self.colors = [
            "#ebedf0",  # Level 0
            "#c6e48b",  # Level 1
            "#7bc96f",  # Level 2
            "#239a3b",  # Level 3
            "#196127",  # Level 4
        ]
        labels = ["0", "1-5", "6-10", "11-15", "16+"]

        for i, (color, label) in enumerate(zip(self.colors, labels)):
            color_box = tk.Canvas(legend_frame, width=15, height=15,
                                  bg=color, highlightthickness=1,
                                  highlightbackground="black")
            color_box.pack(side=tk.LEFT, padx=(5, 0))
            ttk.Label(legend_frame, text=label).pack(side=tk.LEFT,
                                                     padx=(0, 10))
        ttk.Label(legend_frame, text="More commits").pack(side=tk.LEFT)

        # Initialize data structures
        self.repo_base = self.config.get("local_repo_base", "")
        label = self.repo_base if self.repo_base else "(None selected)"
        self.path_label.config(text=f"Repo path: {label}")
        self.day_details = {}  # {date_str: {repo: count}}
        self.rectangles = []   # For cleanup

    # == Core SSH Actions ==
    def _run_ssh_command(self, command_text):
        """Run a command on remote host through SSH"""
        server, user, port, _ssh_dir = self._validate_ssh_inputs()
        cmd = ["ssh", "-p", port, f"{user}@{server}", command_text]
        return subprocess.run(cmd, check=True, capture_output=True, text=True)

    def _remote_cd_cmd(self, ssh_dir):
        ssh_dir = (ssh_dir or "").strip()
        if ssh_dir == "~":
            return 'cd -- "$HOME"'
        if ssh_dir.startswith("~/"):
            rest = ssh_dir[2:].rstrip("/")
            return 'cd -- "$HOME"/' + shlex.quote(rest)
        return f"cd -- {shlex.quote(ssh_dir.rstrip('/'))}"

    def _repo_git_dirname(self, repo_name_no_suffix):
        repo = (repo_name_no_suffix or "").strip().removesuffix(".git")
        return repo + ".git"

    def _remote_path_for_git_url(self, ssh_dir):
        """
        Build an ssh:// URL path segment that works with home-relative dirs.
        Git's ssh URL supports /~/ to mean "home directory".
        """
        ssh_dir = (ssh_dir or "").strip().rstrip("/")
        if ssh_dir == "~":
            return "/~"
        if ssh_dir.startswith("~/"):
            return "/~/" + ssh_dir[2:]
        if ssh_dir.startswith("/"):
            return ssh_dir
        # Treat other relative paths as relative to home
        return "/~/" + ssh_dir

    def list_repos(self):
        self.save_config()

        def work():
            _server, _user, _port, ssh_dir = self._validate_ssh_inputs()
            ssh_dir = ssh_dir.strip()
            # Build a safe 'cd' that still expands "~" on the remote host.
            # Quoting "~" (e.g. 'cd "~/repos"') prevents expansion, so we
            # translate it to $HOME explicitly.
            if ssh_dir == "~":
                cd_cmd = 'cd -- "$HOME"'
            elif ssh_dir.startswith("~/"):
                rest = ssh_dir[2:].rstrip("/")
                # $HOME + "/" + rest, where rest is safely single-quoted.
                cd_cmd = 'cd -- "$HOME"/' + shlex.quote(rest)
            else:
                cd_cmd = f"cd -- {shlex.quote(ssh_dir.rstrip('/'))}"
            cmd = (
                "set -e; "
                f"{cd_cmd}; "
                "for d in *.git; do "
                "  [ -d \"$d\" ] || continue; "
                "  printf '%s\n' \"${d%.git}\"; "
                "done"
            )
            return self._run_ssh_command(cmd).stdout

        def done(stdout):
            self.repo_listbox.delete(0, tk.END)
            for repo in stdout.strip().splitlines():
                repo = repo.strip()
                if repo:
                    self.repo_listbox.insert(tk.END, repo)

        self._run_in_background("List repos", work, done)

    def clone_repo(self):
        selection = self.repo_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection",
                                   "Please select a repo to clone")
            return

        repo_name = self.repo_listbox.get(selection[0])
        clone_path = filedialog.askdirectory(
            title="Select folder to clone into"
        )
        if not clone_path:
            return
        self.save_config()

        def work():
            server, user, port, ssh_dir = self._validate_ssh_inputs()
            dest = str(Path(clone_path) / repo_name)
            url_path = self._remote_path_for_git_url(ssh_dir)
            url = f"ssh://{user}@{server}:{port}{url_path}/{repo_name}.git"
            cmd = ["git", "clone", url, dest]
            return subprocess.run(cmd, check=True, capture_output=True, text=True)

        def done(_result):
            messagebox.showinfo("Success", f"Cloned {repo_name} to {clone_path}")

        self._run_in_background(f"Clone {repo_name}", work, done)

    def create_repo(self):
        """Create a new bare remote repo"""
        repo_name = simpledialog.askstring("Create Repo",
                                           "Enter new repo name:")
        if not repo_name:
            return

        repo_name = repo_name.strip().removesuffix(".git")
        self.save_config()

        def work():
            _server, _user, _port, ssh_dir = self._validate_ssh_inputs()
            cd_cmd = self._remote_cd_cmd(ssh_dir)
            repo_git = shlex.quote(self._repo_git_dirname(repo_name))
            cmd = f"set -e; {cd_cmd}; git init --bare {repo_git}"
            return self._run_ssh_command(cmd)

        def done(_):
            messagebox.showinfo("Success", f"Created {repo_name}.git")
            self.list_repos()

        self._run_in_background(f"Create {repo_name}", work, done)

    def delete_repo(self):
        """Delete a remote repository"""
        selection = self.repo_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection",
                                   "Please select a repo to delete")
            return

        repo_name = self.repo_listbox.get(selection[0])
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Delete remote repo '{repo_name}' permanently?"
        )

        if not confirm:
            return
        self.save_config()

        def work():
            _server, _user, _port, ssh_dir = self._validate_ssh_inputs()
            cd_cmd = self._remote_cd_cmd(ssh_dir)
            repo_git = shlex.quote(self._repo_git_dirname(repo_name))
            cmd = f"set -e; {cd_cmd}; rm -rf {repo_git}"
            return self._run_ssh_command(cmd)

        def done(_):
            messagebox.showinfo("Deleted", f"Removed {repo_name}.git")
            self.list_repos()

        self._run_in_background(f"Delete {repo_name}", work, done)

    def rename_repo(self):
        selection = self.repo_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a repo to rename")
            return

        old_name = self.repo_listbox.get(selection[0]).strip().removesuffix(".git")
        new_name = simpledialog.askstring("Rename Repo", f"Rename '{old_name}' to:")
        if not new_name:
            return
        new_name = new_name.strip().removesuffix(".git")
        if new_name == old_name:
            return

        self.save_config()

        def work():
            _server, _user, _port, ssh_dir = self._validate_ssh_inputs()
            cd_cmd = self._remote_cd_cmd(ssh_dir)
            old_git = shlex.quote(self._repo_git_dirname(old_name))
            new_git = shlex.quote(self._repo_git_dirname(new_name))
            cmd = f"set -e; {cd_cmd}; mv -v {old_git} {new_git}"
            return self._run_ssh_command(cmd)

        def done(_):
            messagebox.showinfo("Success", f"Renamed {old_name} -> {new_name}")
            self.list_repos()

        self._run_in_background(f"Rename {old_name}", work, done)

    def fork_repo(self):
        selection = self.repo_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a repo to copy")
            return

        old_name = self.repo_listbox.get(selection[0]).strip().removesuffix(".git")
        new_name = simpledialog.askstring("Fork/Copy Repo", f"Copy '{old_name}' to:")
        if not new_name:
            return
        new_name = new_name.strip().removesuffix(".git")
        if new_name == old_name:
            return

        self.save_config()

        def work():
            _server, _user, _port, ssh_dir = self._validate_ssh_inputs()
            cd_cmd = self._remote_cd_cmd(ssh_dir)
            old_git = shlex.quote(self._repo_git_dirname(old_name))
            new_git = shlex.quote(self._repo_git_dirname(new_name))
            cmd = f"set -e; {cd_cmd}; cp -R {old_git} {new_git}"
            return self._run_ssh_command(cmd)

        def done(_):
            messagebox.showinfo("Success", f"Copied {old_name} -> {new_name}")
            self.list_repos()

        self._run_in_background(f"Copy {old_name}", work, done)

    def archive_repo(self):
        selection = self.repo_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a repo to archive")
            return

        repo_name = self.repo_listbox.get(selection[0]).strip().removesuffix(".git")
        self.save_config()

        def work():
            _server, _user, _port, ssh_dir = self._validate_ssh_inputs()
            cd_cmd = self._remote_cd_cmd(ssh_dir)
            repo_git = shlex.quote(self._repo_git_dirname(repo_name))
            out_name = shlex.quote(repo_name + ".tgz")
            cmd = f"set -e; {cd_cmd}; tar -czf {out_name} {repo_git}"
            return self._run_ssh_command(cmd)

        def done(_):
            _server, _user, _port, ssh_dir = self._validate_ssh_inputs()
            messagebox.showinfo("Archived", f"Created {ssh_dir.rstrip('/')}/{repo_name}.tgz on remote host")

        self._run_in_background(f"Archive {repo_name}", work, done)

    # == Heatmap Functions ==

    def choose_path(self):
        directory = filedialog.askdirectory(
            title="Select Local Repository Folder"
        )
        if directory:
            self.repo_base = directory
            self.path_label.config(text=f"Repo path: {self.repo_base}")
            self.save_config()

    def generate_heatmap(self):
        if not self.repo_base or not os.path.isdir(self.repo_base):
            messagebox.showwarning(
                "Path Required",
                "Please choose a valid repository folder first.",
            )
            return

        # Clear previous heatmap
        for rect in self.rectangles:
            self.canvas.delete(rect)
        self.rectangles = []
        self.day_details.clear()

        base = Path(os.path.expanduser(self.repo_base))
        repos = [p for p in base.iterdir() if (p / ".git").exists()]

        if not repos:
            messagebox.showwarning("No Repos Found",
                                   "No repositories found in this directory.")
            return

        commit_counter = collections.Counter()
        for repo in repos:
            repo_name = repo.name
            cmd = [
                "git", "-C", str(repo),
                "log", "--date=short", "--format=%ad"
            ]
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, check=True
                )
                for line in result.stdout.splitlines():
                    date_str = line.strip()
                    if date_str:
                        if date_str not in self.day_details:
                            self.day_details[date_str] = \
                                collections.Counter()
                        self.day_details[date_str][repo_name] += 1
                        commit_counter[date_str] += 1
            except subprocess.CalledProcessError:
                continue
            except Exception as e:
                print(f"Error reading {repo}: {e}")

        if not commit_counter:
            messagebox.showwarning("No Data",
                                   "No commits found in the repositories.")
            return

        # Create heatmap visualization
        self.draw_heatmap(commit_counter)

    def draw_heatmap(self, commit_counter):
        # Clear previous drawings
        for rect in self.rectangles:
            self.canvas.delete(rect)
        self.rectangles = []

        # Calculate date range (last 365 days)
        today = datetime.now().date()
        start_date = today - timedelta(days=364)
        days_back = (start_date.weekday() + 1) % 7
        week_start_date = start_date - timedelta(days=days_back)

        # Generate all dates in range
        all_dates = []
        current = week_start_date
        while current <= today:
            all_dates.append(current)
            current += timedelta(days=1)

        # Dimensions
        cell_size = 15
        padding = 2
        label_padding_x = 50
        label_padding_y = 30

        self.canvas.delete("all")

        # Create rectangles for each day
        num_weeks = (len(all_dates) + 6) // 7
        for col in range(num_weeks):
            for day_in_week in range(7):
                current_idx = col * 7 + day_in_week
                if current_idx >= len(all_dates):
                    break

                date = all_dates[current_idx]
                date_str = str(date)
                count = commit_counter.get(date_str, 0)

                # Determine color based on commit count
                if count == 0:
                    color = self.colors[0]
                elif count <= 5:
                    color = self.colors[1]
                elif count <= 10:
                    color = self.colors[2]
                elif count <= 15:
                    color = self.colors[3]
                else:
                    color = self.colors[4]

                # Position with padding for labels
                x1 = label_padding_x + col * (cell_size + padding)
                y1 = day_in_week * (cell_size + padding)
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                rect = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline="",
                    tags=date_str
                )

                # Bind click event
                self.canvas.tag_bind(rect, "<Button-1>",
                                    lambda e, d=date_str:
                                    self.show_day_details(d))

                self.rectangles.append(rect)

        # === Y-AXIS: Weekday labels ===
        day_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, day in enumerate(day_labels):
            y_pos = i * (cell_size + padding) + cell_size / 2
            self.canvas.create_text(
                label_padding_x - 10,
                y_pos,
                text=day,
                anchor="e",
                font=("Arial", 9, "bold"),
                fill="#196127"
            )

        # === X-AXIS: Month labels - Last 12 months ===
        month_y_pos = 7 * (cell_size + padding) + 10

        # Build list of last 12 months working backwards from today
        months_to_show = []
        current_month = today.replace(day=1)
        for _ in range(12):
            months_to_show.insert(0, (current_month.month, current_month.year))
            current_month -= timedelta(days=1)
            current_month = current_month.replace(day=1)

        months_to_show_set = set(months_to_show)

        # Label only the first occurrence of each month
        labeled_months = set()
        for col in range(num_weeks):
            current_idx = col * 7
            if current_idx < len(all_dates):
                date = all_dates[current_idx]
                month_year = (date.month, date.year)

                if (month_year in months_to_show_set and
                    month_year not in labeled_months):
                    x_pos = (label_padding_x +
                            col * (cell_size + padding) + cell_size / 2)
                    month_label = date.strftime("%b")
                    self.canvas.create_text(
                        x_pos,
                        month_y_pos,
                        text=month_label,
                        anchor="n",
                        font=("Arial", 9, "bold"),
                        fill="#196127"
                    )
                    labeled_months.add(month_year)

        # === Axis lines for clarity ===
        heatmap_width = label_padding_x + num_weeks * (cell_size + padding)
        heatmap_height = 7 * (cell_size + padding)

        self.canvas.create_line(
            label_padding_x - 5, 0,
            label_padding_x - 5, heatmap_height,
            fill="gray", width=1, dash=(2, 2)
        )
        self.canvas.create_line(
            label_padding_x, heatmap_height + 5,
            heatmap_width, heatmap_height + 5,
            fill="gray", width=1, dash=(2, 2)
        )

        # Set scroll region
        total_width = heatmap_width + 20
        total_height = heatmap_height + label_padding_y + 40
        self.canvas.config(scrollregion=(0, 0, total_width, total_height))

    def show_day_details(self, date_str):
        """Show popup with repos that committed on this day"""
        details = self.day_details.get(date_str, {})
        total = sum(details.values())

        if not details:
            messagebox.showinfo(date_str, "No commits on this day.")
            return

        # Build message: sorted by count descending
        msg = f"Date: {date_str}\nTotal: {total} commits\n\n"
        for repo, count in sorted(
            details.items(), key=lambda x: x[1], reverse=True
        ):
            msg += f"- {repo}: {count} commits\n"

        # Show in a scrollable text window
        top = tk.Toplevel(self.root)
        top.title(f"Commits on {date_str}")
        top.geometry("400x300")

        text = tk.Text(top, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(tk.END, msg)
        text.config(state=tk.DISABLED)

        scrollbar = ttk.Scrollbar(text, orient=tk.VERTICAL,
                                  command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


if __name__ == "__main__":
    root = tk.Tk()
    app = GithelperGUI(root)
    root.mainloop()