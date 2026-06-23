#!/usr/bin/env python3
import subprocess
import re
from pathlib import Path

CHANGELOG = Path("CHANGELOG.md")

TEMPLATE_HEADER = """# Changelog

All notable changes to this project will be documented in this file.

"""

SECTION_ORDER = [
    ("feat", "✨ Features"),
    ("fix", "🐛 Fixes"),
    ("docs", "📝 Documentation"),
    ("refactor", "♻️ Refactoring"),
    ("test", "🧪 Tests"),
    ("chore", "🔧 Chores"),
]

def get_git_log():
    """Return commit messages since the beginning (no tags yet)."""
    result = subprocess.run(
        ["git", "log", "--pretty=format:%s"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.splitlines()

def categorize(commits):
    buckets = {key: [] for key, _ in SECTION_ORDER}

    for msg in commits:
        m = re.match(r"^(feat|fix|docs|refactor|test|chore)(\(.+\))?:\s*(.*)", msg)
        if m:
            key, _, text = m.groups()
            buckets[key].append(text)
        else:
            buckets.setdefault("other", []).append(msg)

    return buckets

def write_changelog(buckets):
    lines = [TEMPLATE_HEADER, "## Unreleased\n"]

    for key, title in SECTION_ORDER:
        items = buckets.get(key, [])
        if items:
            lines.append(f"### {title}\n")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")

    if buckets.get("other"):
        lines.append("### Other\n")
        for item in buckets["other"]:
            lines.append(f"- {item}")
        lines.append("")

    CHANGELOG.write_text("\n".join(lines).strip() + "\n")

def main():
    commits = get_git_log()
    buckets = categorize(commits)
    write_changelog(buckets)
    print("CHANGELOG.md generated.")

if __name__ == "__main__":
    main()
