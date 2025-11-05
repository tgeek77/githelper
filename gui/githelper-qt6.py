#!/usr/bin/python3
"""
Git Helper - PyQt6 version with Local Commit Heatmap
"""

import subprocess
import sys
import os
import json
import collections
from datetime import datetime, timedelta
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QMessageBox,
    QFileDialog,
    QInputDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

CONFIG_PATH = Path.home() / ".githelperrc"


class GitHelperGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Git Helper - Manage Remote Repos")
        self.resize(550, 420)

        self.config = self.load_config()

        # --- Layouts
        main_layout = QVBoxLayout()
        ssh_group = QGroupBox("SSH Settings")
        ssh_layout = QVBoxLayout()

        # --- First row: Server, User, Port (3 columns)
        top_row = QHBoxLayout()

        server_container = QVBoxLayout()
        server_container.addWidget(QLabel("Server:"))
        self.server_entry = QLineEdit()
        self.server_entry.setText(self.config.get("server", "example.com"))
        server_container.addWidget(self.server_entry)
        top_row.addLayout(server_container)

        user_container = QVBoxLayout()
        user_container.addWidget(QLabel("User:"))
        self.user_entry = QLineEdit()
        self.user_entry.setText(self.config.get("user", "tux"))
        user_container.addWidget(self.user_entry)
        top_row.addLayout(user_container)

        port_container = QVBoxLayout()
        port_container.addWidget(QLabel("Port:"))
        self.port_entry = QLineEdit()
        self.port_entry.setText(self.config.get("port", "22"))
        port_container.addWidget(self.port_entry)
        top_row.addLayout(port_container)

        ssh_layout.addLayout(top_row)

        # --- Second row: Directory
        dir_row = QHBoxLayout()
        dir_row.addWidget(QLabel("Directory:"))
        self.dir_entry = QLineEdit()
        self.dir_entry.setText(self.config.get("dir", "~/repos"))
        dir_row.addWidget(self.dir_entry)
        ssh_layout.addLayout(dir_row)

        # --- Buttons
        button_row = QHBoxLayout()
        list_button = QPushButton("List Repos")
        clone_button = QPushButton("Clone")
        create_button = QPushButton("Create Repo")
        delete_button = QPushButton("Delete Repo")

        for btn, func in [
            (list_button, self.list_repos),
            (clone_button, self.clone_repo),
            (create_button, self.create_repo),
            (delete_button, self.delete_repo),
        ]:
            btn.clicked.connect(func)
            button_row.addWidget(btn)

        ssh_layout.addLayout(button_row)
        ssh_group.setLayout(ssh_layout)
        main_layout.addWidget(ssh_group)

        # --- Repo list
        repo_group = QGroupBox("Repositories")
        repo_layout = QVBoxLayout()
        self.repo_list = QListWidget()
        repo_layout.addWidget(self.repo_list)
        repo_group.setLayout(repo_layout)
        main_layout.addWidget(repo_group)

        # --- New Heatmap Button (at bottom)
        heatmap_button = QPushButton("Local Commit Heatmap")
        heatmap_button.clicked.connect(self.show_heatmap_window)
        main_layout.addWidget(heatmap_button)

        self.setLayout(main_layout)

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
            "server": self.server_entry.text(),
            "user": self.user_entry.text(),
            "port": self.port_entry.text(),
            "dir": self.dir_entry.text(),
        }
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to save config: {e}")

    # == Core SSH Actions ==
    def _run_ssh_command(self, command_text):
        """Run a command on remote host through SSH"""
        server = self.server_entry.text()
        user = self.user_entry.text()
        port = self.port_entry.text()

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
            ssh_dir = self.dir_entry.text()
            cmd = f"ls {ssh_dir}/ | sed -e 's/\\.git//g'"
            result = self._run_ssh_command(cmd)
            self.repo_list.clear()
            for repo in result.stdout.strip().splitlines():
                if repo:
                    self.repo_list.addItem(repo)
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"SSH list failed:\n{e.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def clone_repo(self):
        item = self.repo_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No Selection",
                                "Please select a repo to clone")
            return

        repo_name = item.text()
        clone_path = QFileDialog.getExistingDirectory(
            self, "Select folder to clone into"
        )
        if not clone_path:
            return

        server = self.server_entry.text()
        user = self.user_entry.text()
        port = self.port_entry.text()
        ssh_dir = self.dir_entry.text()

        cmd = (
            f"git clone ssh://{user}@{server}:{port}/{ssh_dir}/"
            f"{repo_name}.git {clone_path}/{repo_name}"
        )

        try:
            subprocess.run(cmd, shell=True, check=True,
                           capture_output=True, text=True)
            QMessageBox.information(
                self, "Success", f"Cloned {repo_name} to {clone_path}"
            )
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Clone Failed", f"Error:\n{e.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def create_repo(self):
        """Create a new bare remote repo"""
        text, ok = QInputDialog.getText(self, "Create Repo",
                                        "Enter new repo name:")
        if not ok or not text:
            return

        repo_name = text.strip()
        if not repo_name.endswith(".git"):
            repo_name = repo_name + ".git"

        ssh_dir = self.dir_entry.text()
        try:
            cmd = f"git init --bare {ssh_dir}/{repo_name}"
            self._run_ssh_command(cmd)
            QMessageBox.information(self, "Success", f"Created {repo_name}")
            self.list_repos()
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error",
                                 f"Failed to create repo:\n{e.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_repo(self):
        """Delete a remote repository"""
        item = self.repo_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No Selection",
                                "Please select a repo to delete")
            return

        repo_name = item.text()
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Delete remote repo '{repo_name}' permanently?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.No:
            return

        ssh_dir = self.dir_entry.text()
        try:
            cmd = f"rm -rf {ssh_dir}/{repo_name}.git"
            self._run_ssh_command(cmd)
            QMessageBox.information(self, "Deleted", f"Removed {repo_name}")
            self.list_repos()
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error",
                                 f"Failed to delete repo:\n{e.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # == Open Heatmap Window ==
    def show_heatmap_window(self):
        self.heatmap_window = CommitHeatmapWindow()
        self.heatmap_window.show()


class CommitHeatmapWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Local Commit Heatmap")
        self.resize(850, 400)

        self.config = self.load_config()
        self.repo_base = self.config.get("local_repo_base", "")

        # Data storage for per-day details
        self.day_details = {}  # {date_str: {repo: count}}
        self.cell_to_date = {}  # {(row, col): date_str}

        main_layout = QVBoxLayout()

        # --- Controls
        control_box = QGroupBox("Controls")
        ctrl_layout = QHBoxLayout()
        self.path_label = QLabel(
            f"Repo path: {self.repo_base or '(None selected)'}"
        )
        choose_path_btn = QPushButton("Choose Repos Folder")
        choose_path_btn.clicked.connect(self.choose_path)
        generate_btn = QPushButton("Generate Heatmap")
        generate_btn.clicked.connect(self.generate_heatmap)
        ctrl_layout.addWidget(self.path_label)
        ctrl_layout.addWidget(choose_path_btn)
        ctrl_layout.addWidget(generate_btn)
        control_box.setLayout(ctrl_layout)
        main_layout.addWidget(control_box)

        # --- Table
        self.table = QTableWidget(7, 53)
        self.table.verticalHeader().setDefaultSectionSize(15)
        self.table.horizontalHeader().setDefaultSectionSize(15)
        self.table.setVerticalHeaderLabels(
            ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        )
        self.table.itemClicked.connect(self.show_day_details)

        main_layout.addWidget(self.table)

        # --- Legend
        legend_layout = QHBoxLayout()
        legend_label = QLabel("Fewer commits")
        legend_layout.addWidget(legend_label)
        shades = [0, 3, 6, 9, 12]
        for i, max_commits in enumerate(shades):
            color_box = QLabel()
            color_box.setFixedSize(15, 15)
            intensity = 255 - (i * 50)
            color = (
                QColor(200, intensity, 200)
                if i > 0
                else QColor(230, 230, 230)
            )
            color_box.setStyleSheet(
                f"background-color: rgb({color.red()}, "
                f"{color.green()}, {color.blue()});"
            )
            legend_layout.addWidget(color_box)
            if i == 0:
                legend_layout.addWidget(QLabel("0 commits"))
            else:
                legend_layout.addWidget(
                    QLabel(f"{shades[i-1]+1}-{max_commits} commits")
                )
        legend_layout.addWidget(QLabel("More commits"))
        legend_layout.addStretch()
        main_layout.addLayout(legend_layout)

        self.setLayout(main_layout)

    # ---------------------------
    def load_config(self):
        try:
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def save_config(self):
        self.config["local_repo_base"] = self.repo_base
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Save Error", str(e))

    def choose_path(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Local Repository Folder"
        )
        if directory:
            self.repo_base = directory
            self.path_label.setText(f"Repo path: {self.repo_base}")
            self.save_config()

    # ---------------------------
    def generate_heatmap(self):
        if not self.repo_base or not os.path.isdir(self.repo_base):
            QMessageBox.warning(
                self,
                "Path Required",
                "Please choose a valid repository folder first.",
            )
            return

        self.table.clearContents()
        self.table.setToolTip("")
        self.day_details.clear()
        self.cell_to_date.clear()

        base = Path(os.path.expanduser(self.repo_base))
        repos = [p for p in base.iterdir() if (p / ".git").exists()]

        if not repos:
            QMessageBox.warning(self, "No Repos Found",
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
                            self.day_details[date_str] = (
                                collections.Counter()
                            )
                        self.day_details[date_str][repo_name] += 1
                        commit_counter[date_str] += 1
            except subprocess.CalledProcessError:
                continue
            except Exception as e:
                print(f"Error reading {repo}: {e}")

        if not commit_counter:
            QMessageBox.warning(self, "No Data",
                                "No commits found in the repositories.")
            return

        today = datetime.now().date()
        start_date = today - timedelta(days=364)

        # Find Sunday at or before start_date to align weeks properly
        days_back = (start_date.weekday() + 1) % 7
        week_start_date = start_date - timedelta(days=days_back)

        # Generate sequential dates from Sunday to today
        all_dates = []
        current = week_start_date
        while current <= today:
            all_dates.append(current)
            current += timedelta(days=1)

        max_commits = max(commit_counter.values() or [1])

        # Set month labels
        horizontal_labels = [""] * 53
        for col in range(53):
            week_start_idx = col * 7
            if week_start_idx < len(all_dates):
                date = all_dates[week_start_idx]
                if col == 0 or date.day <= 7:
                    horizontal_labels[col] = date.strftime("%b")

        self.table.setHorizontalHeaderLabels(horizontal_labels)

        # Fill grid: each column is a week, each row is a day
        col = 0
        for week_start_idx in range(0, len(all_dates), 7):
            for day_in_week in range(7):
                current_idx = week_start_idx + day_in_week
                if current_idx >= len(all_dates):
                    break
                date = all_dates[current_idx]
                date_str = str(date)
                count = commit_counter.get(date_str, 0)

                item = QTableWidgetItem()
                if count > 0:
                    intensity = int(
                        255 - (min(1, count / max_commits) * 200)
                    )
                    color = QColor(200, intensity, 200)
                    item.setBackground(color)
                    tooltip = f"{date}: {count} commit(s)"
                else:
                    color = QColor(230, 230, 230)
                    item.setBackground(color)
                    tooltip = f"{date}: no commits"

                item.setToolTip(tooltip)
                row = day_in_week
                self.table.setItem(row, col, item)
                self.cell_to_date[(row, col)] = date_str
            col += 1

    def show_day_details(self, item):
        """Show popup with repos that committed on this day"""
        row = item.row()
        col = item.column()

        date_str = self.cell_to_date.get((row, col))
        if not date_str:
            QMessageBox.warning(self, "Error",
                                "Could not determine date.")
            return

        details = self.day_details.get(date_str, {})
        total = sum(details.values())

        if not details:
            QMessageBox.information(self, f"{date_str}",
                                    "No commits on this day.")
            return

        # Build message: sorted by count descending
        msg = f"Date: {date_str}\nTotal: {total} commits\n\n"
        for repo, count in sorted(
            details.items(), key=lambda x: x[1], reverse=True
        ):
            msg += f"- {repo}: {count} commits\n"

        QMessageBox.information(self, f"Commits on {date_str}", msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = GitHelperGUI()
    win.show()
    sys.exit(app.exec())
