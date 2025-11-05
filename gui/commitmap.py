#!/usr/bin/python3
"""
Commit Heatmap - Standalone GitHub-style Local Commit Heatmap
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
    QPushButton,
    QMessageBox,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

CONFIG_PATH = Path.home() / ".githelperrc"  # Shared with Git Helper app


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

        # Define color levels (approximating GitHub style, extended for more buckets)
        self.colors = [
            QColor(235, 237, 240),  # Level 0: no commits (light gray)
            QColor(201, 240, 212),  # Level 1: very light green
            QColor(127, 213, 148),  # Level 2: light green
            QColor(38, 166, 91),    # Level 3: medium green
            QColor(0, 109, 44),     # Level 4: dark green
            QColor(0, 68, 27),      # Level 5: very dark green
        ]

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
        label_texts = [
            "0 commits",
            "1-5 commits",
            "6-10 commits",
            "11-15 commits",
            "16-20 commits",
            "21+ commits",  # Adjusted to 21+ for the last bucket
        ]
        for i in range(len(self.colors)):
            color_box = QLabel()
            color_box.setFixedSize(15, 15)
            color = self.colors[i]
            color_box.setStyleSheet(
                f"background-color: rgb({color.red()}, "
                f"{color.green()}, {color.blue()});"
            )
            legend_layout.addWidget(color_box)
            legend_layout.addWidget(QLabel(label_texts[i]))
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
                # Determine color based on discrete buckets
                if count == 0:
                    color = self.colors[0]
                elif count <= 5:
                    color = self.colors[1]
                elif count <= 10:
                    color = self.colors[2]
                elif count <= 15:
                    color = self.colors[3]
                elif count <= 20:
                    color = self.colors[4]
                else:
                    color = self.colors[5]  # 21 or more
                item.setBackground(color)
                item.setToolTip(f"{date}: {count} commit(s)")

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
    win = CommitHeatmapWindow()
    win.show()
    sys.exit(app.exec())
