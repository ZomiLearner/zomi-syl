#!/usr/bin/env python3
import subprocess
import re
from pathlib import Path
from datetime import date
from typing import Dict, List, Tuple, Optional

import tomllib  # Python 3.11+

def get_version_from_pyproject(pyproject_path: Path = Path("pyproject.toml")) -> str:
    """Extract the project version from pyproject.toml."""
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found.")

    data = tomllib.loads(pyproject_path.read_text())

    # PEP 621 standard location
    try:
        return data["project"]["version"]
    except KeyError:
        raise KeyError("Version not found in [project] section of pyproject.toml.")


CHANGELOG = Path("CHANGELOG.md")

TEMPLATE_HEADER = """# Changelog

All notable changes to this project will be documented in this file.

"""

SECTION_ORDER: List[Tuple[str, str]] = [
    ("feat", "✨ Features"),
    ("fix", "🐛 Fixes"),
    ("docs", "📝 Documentation"),
    ("refactor", "♻️ Refactoring"),
    ("test", "🧪 Tests"),
    ("chore", "🔧 Chores"),
]

COMMIT_REGEX = re.compile(
    r"^(?P<type>feat|fix|docs|refactor|test|chore)"
    r"(?:\((?P<scope>[^)]+)\))?:\s*(?P<message>.+)"
)

def run_git_command(args: List[str]) -> List[str]:
    """Run a git command safely and return output lines."""
    try:
        result = subprocess.run(
            ["git", "log", "--pretty=format:%s"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.splitlines()

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Git command failed: {e}") from e

def get_git_log() -> List[str]:
    """Return commit messages since the beginning."""
    return run_git_command(["log", "--pretty=format:%s"])

def categorize(commits: List[str]) -> Dict[str, List[str]]:
    """Categorize commit messages into buckets."""
    buckets: Dict[str, List[str]] = {key: [] for key, _ in SECTION_ORDER}
    buckets["other"] = []

    for msg in commits:
        match = COMMIT_REGEX.match(msg)
        if match:
            commit_type = match.group("type")
            scope = match.group("scope")
            message = match.group("message")

            full_message = f"{scope}: {message}" if scope else message
            buckets[commit_type].append(full_message)
        else:
            buckets["other"].append(msg)

    return buckets

def generate_section(title: str, items: List[str]) -> str:
    """Generate a markdown section for a category."""
    if not items:
        return ""
    lines = [f"### {title}", ""]
    lines.extend(f"- {item}" for item in items)
    lines.append("")
    return "\n".join(lines)

def write_changelog(buckets: Dict[str, List[str]]) -> None:
    """Write the changelog file."""
    version = get_version_from_pyproject()
    today = date.today().isoformat()

    lines = [
        TEMPLATE_HEADER,
        f"## [{version}] - {today}\n",
    ]

    for key, title in SECTION_ORDER:
        section = generate_section(title, buckets.get(key, []))
        if section:
            lines.append(section)

    if buckets["other"]:
        lines.append(generate_section("Other", buckets["other"]))

    CHANGELOG.write_text("\n".join(lines).strip() + "\n")

def main() -> None:
    try:
        commits = get_git_log()
    except RuntimeError as err:
        print(err)
        return

    if not commits:
        print("No commits found.")
        return

    buckets = categorize(commits)
    write_changelog(buckets)
    print("CHANGELOG.md generated.")

if __name__ == "__main__":
    main()
