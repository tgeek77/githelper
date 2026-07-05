"""Local commit heatmap aggregation and terminal rendering."""

import collections
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

from githelper.errors import GithelperError

BUCKETS = [
    (0, 0),
    (1, 5),
    (6, 10),
    (11, 15),
    (16, None),
]

ANSI_COLORS = [
    "\033[38;5;252m",  # level 0
    "\033[38;5;156m",  # level 1
    "\033[38;5;114m",  # level 2
    "\033[38;5;71m",   # level 3
    "\033[38;5;22m",   # level 4
]
ANSI_RESET = "\033[0m"

ASCII_CHARS = [".", "o", "O", "@", "#"]


def bucket_for_count(count):
    """Return bucket index for a commit count."""
    if count == 0:
        return 0
    if count <= 5:
        return 1
    if count <= 10:
        return 2
    if count <= 15:
        return 3
    return 4


def discover_repos(base_path):
    """Find git repos one level deep under base_path (matches GUI heatmap tab)."""
    base = Path(os.path.expanduser(base_path)).resolve()
    if not base.is_dir():
        raise GithelperError(f"Base folder is not a directory: {base}")
    repos = [p for p in base.iterdir() if p.is_dir() and (p / ".git").is_dir()]
    if not repos:
        raise GithelperError(f"No repositories found in {base}")
    return repos


def aggregate_commits(base_path):
    """
    Aggregate commit counts by date across repos under base_path.

    Returns (commit_counter, day_details) where day_details maps
    date_str -> {repo_name: count}.
    """
    repos = discover_repos(base_path)
    commit_counter = collections.Counter()
    day_details = {}

    for repo in repos:
        repo_name = repo.name
        cmd = [
            "git", "-C", str(repo),
            "log", "--all", "--date=short", "--format=%ad",
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError:
            continue
        for line in result.stdout.splitlines():
            date_str = line.strip()
            if not date_str:
                continue
            day_details.setdefault(date_str, collections.Counter())[repo_name] += 1
            commit_counter[date_str] += 1

    if not commit_counter:
        raise GithelperError("No commits found in the repositories.")
    return commit_counter, day_details


def heatmap_dates(today=None):
    """Generate aligned week grid dates for the last 365 days."""
    today = today or datetime.now().date()
    start_date = today - timedelta(days=364)
    days_back = (start_date.weekday() + 1) % 7
    week_start_date = start_date - timedelta(days=days_back)

    all_dates = []
    current = week_start_date
    while current <= today:
        all_dates.append(current)
        current += timedelta(days=1)
    return all_dates, today


def export_json(commit_counter, day_details):
    """Export heatmap data as a JSON-serializable dict."""
    data = {}
    for date_str, total in sorted(commit_counter.items()):
        repos = day_details.get(date_str, {})
        data[date_str] = {
            "total": total,
            "repos": dict(sorted(repos.items())),
        }
    return data


def format_day_breakdown(day_details, date_str):
    """Format per-repo breakdown for a single day."""
    details = day_details.get(date_str, {})
    total = sum(details.values())
    if not details:
        return f"Date: {date_str}\nNo commits on this day.\n"
    lines = [f"Date: {date_str}", f"Total: {total} commits", ""]
    for repo, count in sorted(details.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"- {repo}: {count} commits")
    return "\n".join(lines) + "\n"


def render_heatmap(commit_counter, use_color=True):
    """Render a GitHub-style heatmap grid for the terminal."""
    all_dates, today = heatmap_dates()
    num_weeks = (len(all_dates) + 6) // 7
    is_tty = use_color and sys.stdout.isatty()

    lines = []
    legend = "Legend: " + " ".join(
        f"{label}={char}"
        for label, char in zip(["0", "1-5", "6-10", "11-15", "16+"], ASCII_CHARS)
    )
    lines.append(legend)
    lines.append("")

    day_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for day_in_week, label in enumerate(day_labels):
        row = f"{label:>3} "
        for col in range(num_weeks):
            idx = col * 7 + day_in_week
            if idx >= len(all_dates):
                row += "  "
                continue
            date = all_dates[idx]
            count = commit_counter.get(str(date), 0)
            level = bucket_for_count(count)
            if is_tty:
                cell = f"{ANSI_COLORS[level]}██{ANSI_RESET}"
            else:
                cell = ASCII_CHARS[level] + " "
            row += cell
        lines.append(row)

    month_row = "    "
    labeled_months = set()
    months_to_show = set()
    current_month = today.replace(day=1)
    for _ in range(12):
        months_to_show.add((current_month.month, current_month.year))
        current_month -= timedelta(days=1)
        current_month = current_month.replace(day=1)

    for col in range(num_weeks):
        idx = col * 7
        if idx >= len(all_dates):
            month_row += "  "
            continue
        date = all_dates[idx]
        month_year = (date.month, date.year)
        if month_year in months_to_show and month_year not in labeled_months:
            month_row += date.strftime("%b")[:2].ljust(2)
            labeled_months.add(month_year)
        else:
            month_row += "  "

    lines.append(month_row)
    return "\n".join(lines) + "\n"


def dumps_json(data):
    return json.dumps(data, indent=2) + "\n"
