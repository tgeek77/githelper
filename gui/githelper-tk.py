#!/usr/bin/python3
"""
Git Helper - tkinter version with Local Commit Heatmap
"""

import subprocess
import os
import json
import collections
from datetime import datetime, timedelta
from pathlib import Path
import tkinter as tk
from tkinter import (
    ttk, messagebox, filedialog, simpledialog
)


CONFIG_PATH = Path.home() / ".githelperrc"


class GitHelperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Git Helper - Manage Remote Repos")
        self.root.geometry("600x500")

        self.config = self.load_config()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Main tab
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Remote Repos")

        # Heatmap tab
        self.heatmap_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.heatmap_frame, text="Local Commit Heatmap")

        self.create_main_tab()
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
        cfg = {
            "server": self.server_var.get(),
            "user": self.user_var.get(),
            "port": self.port_var.get(),
            "dir": self.dir_var.get(),
        }
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
        except Exception as e:
            messagebox.showwarning("Warning", f"Failed to save config: {e}")

    # == Main Tab UI ==
    def create_main_tab(self):
        # SSH Settings Group
        ssh_frame = ttk.LabelFrame(self.main_frame, text="SSH Settings")
        ssh_frame.pack(fill=tk.X, padx=10, pady=10)

        # Server/User/Port row
        top_row = ttk.Frame(ssh_frame)
        top_row.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(top_row, text="Server:").pack(side=tk.LEFT)
        self.server_var = tk.StringVar(value=self.config.get("server", "example.com"))
        ttk.Entry(top_row, textvariable=self.server_var, width=15).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(top_row, text="User:").pack(side=tk.LEFT)
        self.user_var = tk.StringVar(value=self.config.get("user", "tux"))
        ttk.Entry(top_row, textvariable=self.user_var, width=10).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(top_row, text="Port:").pack(side=tk.LEFT)
        self.port_var = tk.StringVar(value=self.config.get("port", "22"))
        ttk.Entry(top_row, textvariable=self.port_var, width=5).pack(side=tk.LEFT)

        # Directory row
        dir_row = ttk.Frame(ssh_frame)
        dir_row.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(dir_row, text="Directory:").pack(side=tk.LEFT)
        self.dir_var = tk.StringVar(value=self.config.get("dir", "~/repos"))
        ttk.Entry(dir_row, textvariable=self.dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Buttons row
        button_row = ttk.Frame(ssh_frame)
        button_row.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_row, text="List Repos", command=self.list_repos).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_row, text="Clone", command=self.clone_repo).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_row, text="Create Repo", command=self.create_repo).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_row, text="Delete Repo", command=self.delete_repo).pack(side=tk.LEFT)

        # Repositories list
        repo_frame = ttk.LabelFrame(self.main_frame, text="Repositories")
        repo_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.repo_listbox = tk.Listbox(repo_frame)
        self.repo_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # == Heatmap Tab UI ==
    def create_heatmap_tab(self):
        # Controls
        control_frame = ttk.Frame(self.heatmap_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        self.path_label = ttk.Label(control_frame, text="Repo path: (None selected)")
        self.path_label.pack(side=tk.LEFT)

        ttk.Button(control_frame, text="Choose Folder", command=self.choose_path).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Generate Heatmap", command=self.generate_heatmap).pack(side=tk.LEFT, padx=5)

        # Heatmap display
        heatmap_container = ttk.Frame(self.heatmap_frame)
        heatmap_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Canvas for heatmap
        self.canvas = tk.Canvas(heatmap_container, bg="white")
        v_scroll = ttk.Scrollbar(heatmap_container, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scroll = ttk.Scrollbar(heatmap_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

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
            color_box = tk.Canvas(legend_frame, width=15, height=15, bg=color, highlightthickness=1, highlightbackground="black")
            color_box.pack(side=tk.LEFT, padx=(5, 0))
            ttk.Label(legend_frame, text=label).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(legend_frame, text="More commits").pack(side=tk.LEFT)

        # Initialize data structures
        self.repo_base = self.config.get("local_repo_base", "")
        self.path_label.config(text=f"Repo path: {self.repo_base or '(None selected)'}")
        self.day_details = {}  # {date_str: {repo: count}}
        self.rectangles = []   # For cleanup

    # == Core SSH Actions ==
    def _run_ssh_command(self, command_text):
        """Run a command on remote host through SSH"""
        server = self.server_var.get()
        user = self.user_var.get()
        port = self.port_var.get()

        full_cmd = f"ssh {user}@{server} -p {port} '{command_text}'"

        return subprocess.run(
            full_cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
        )

    def list_repos(self):
        self.save_config()  # auto-save settings each time
        try:
            ssh_dir = self.dir_var.get()
            cmd = f"ls {ssh_dir}/ | sed -e 's/\\.git//g'"
            result = self._run_ssh_command(cmd)
            self.repo_listbox.delete(0, tk.END)
            for repo in result.stdout.strip().splitlines():
                if repo:
                    self.repo_listbox.insert(tk.END, repo)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"SSH list failed:\n{e.stderr}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clone_repo(self):
        selection = self.repo_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a repo to clone")
            return

        repo_name = self.repo_listbox.get(selection[0])
        clone_path = filedialog.askdirectory(title="Select folder to clone into")
        if not clone_path:
            return

        server = self.server_var.get()
        user = self.user_var.get()
        port = self.port_var.get()
        ssh_dir = self.dir_var.get()

        cmd = (
            f"git clone ssh://{user}@{server}:{port}/{ssh_dir}/"
            f"{repo_name}.git {clone_path}/{repo_name}"
        )

        try:
            subprocess.run(cmd, shell=True, check=True,
                           capture_output=True, text=True)
            messagebox.showinfo("Success", f"Cloned {repo_name} to {clone_path}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Clone Failed", f"Error:\n{e.stderr}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_repo(self):
        """Create a new bare remote repo"""
        repo_name = simpledialog.askstring("Create Repo", "Enter new repo name:")
        if not repo_name:
            return

        repo_name = repo_name.strip()
        if not repo_name.endswith(".git"):
            repo_name = repo_name + ".git"

        ssh_dir = self.dir_var.get()
        try:
            cmd = f"git init --bare {ssh_dir}/{repo_name}"
            self._run_ssh_command(cmd)
            messagebox.showinfo("Success", f"Created {repo_name}")
            self.list_repos()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to create repo:\n{e.stderr}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_repo(self):
        """Delete a remote repository"""
        selection = self.repo_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a repo to delete")
            return

        repo_name = self.repo_listbox.get(selection[0])
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Delete remote repo '{repo_name}' permanently?"
        )

        if not confirm:
            return

        ssh_dir = self.dir_var.get()
        try:
            cmd = f"rm -rf {ssh_dir}/{repo_name}.git"
            self._run_ssh_command(cmd)
            messagebox.showinfo("Deleted", f"Removed {repo_name}")
            self.list_repos()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to delete repo:\n{e.stderr}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # == Heatmap Functions ==
    def save_config(self):
        self.config["server"] = self.server_var.get()
        self.config["user"] = self.user_var.get()
        self.config["port"] = self.port_var.get()
        self.config["dir"] = self.dir_var.get()
        self.config["local_repo_base"] = self.repo_base
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            messagebox.showwarning("Save Error", str(e))

    def choose_path(self):
        directory = filedialog.askdirectory(title="Select Local Repository Folder")
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
            messagebox.showwarning("No Repos Found", "No repositories found in this directory.")
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
                            self.day_details[date_str] = collections.Counter()
                        self.day_details[date_str][repo_name] += 1
                        commit_counter[date_str] += 1
            except subprocess.CalledProcessError:
                continue
            except Exception as e:
                print(f"Error reading {repo}: {e}")

        if not commit_counter:
            messagebox.showwarning("No Data", "No commits found in the repositories.")
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

        # Draw heatmap
        cell_size = 15
        padding = 2
        self.canvas.delete("all")
        
        # Create rectangles for each day
        for col, week_start_idx in enumerate(range(0, len(all_dates), 7)):
            for day_in_week in range(7):
                current_idx = week_start_idx + day_in_week
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
                
                x1 = col * (cell_size + padding)
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
                                    lambda e, d=date_str: self.show_day_details(d))
                
                self.rectangles.append(rect)

        # Set scroll region
        max_x = ((len(all_dates) // 7) + 1) * (cell_size + padding)
        max_y = 7 * (cell_size + padding)
        self.canvas.config(scrollregion=(0, 0, max_x, max_y))

        # Add month labels
        month_y = max_y + 20
        for col, week_start_idx in enumerate(range(0, len(all_dates), 7)):
            week_start = all_dates[week_start_idx]
            if col == 0 or week_start.day <= 7:
                month_name = week_start.strftime("%b")
                self.canvas.create_text(
                    col * (cell_size + padding) + cell_size/2,
                    month_y,
                    text=month_name,
                    anchor="n"
                )

        # Add weekday labels
        day_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        label_x = -20
        for i, day in enumerate(day_labels):
            y_pos = i * (cell_size + padding) + cell_size/2
            self.canvas.create_text(label_x, y_pos, text=day, anchor="e")

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

        scrollbar = ttk.Scrollbar(text, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


if __name__ == "__main__":
    root = tk.Tk()
    app = GitHelperGUI(root)
    root.mainloop()
