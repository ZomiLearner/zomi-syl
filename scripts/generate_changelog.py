#!/usr/bin/env python3
import argparse
import subprocess
import re
from pathlib import Path
from datetime import date
import tomllib

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

COMMIT_REGEX = re.compile(
    r"^(?P<type>feat|fix|docs|refactor|test|chore)"
    r"(?P<breaking>!)?"
    r"(?:\((?P<scope>[^)]+)\))?:\s*(?P<message>.+)"
)

def run_git(args):
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()

def get_version_from_pyproject(pyproject_path: Path = Path("pyproject.toml")) -> str:
    """Extract the project version from pyproject.toml."""
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found.")

    data = tomllib.loads(pyproject_path.read_text())

    try:
        return data["project"]["version"]
    except KeyError:
        raise KeyError("Version not found in [project] section of pyproject.toml.")

def get_tags():
    """Return tags sorted by creation date (oldest first)."""
    tags = run_git(["tag", "--list", "--sort=creatordate"]).splitlines()
    return tags

def get_commits_between(start_tag, end_tag):
    """Return commit messages between two tags."""
    if start_tag:
        range_expr = f"{start_tag}..{end_tag}"
    else:
        range_expr = end_tag  # from beginning

    output = run_git(["log", range_expr, "--pretty=format:%s"])
    return output.splitlines() if output else []

def create_git_tag(version):
    """Create a git tag for the new release."""
    run_git(["tag", f"v{version}"])
    print(f"Created git tag: {version}")

def get_unreleased_commits(latest_tag):
    """Commits after the latest tag."""
    output = run_git(["log", f"{latest_tag}..HEAD", "--pretty=format:%s"])
    return output.splitlines() if output else []

def generate_breaking_section(items):
    if not items:
        return ""
    lines = ["### ⚠️ Breaking Changes", ""]
    lines.extend(f"- {item}" for item in items)
    lines.append("")
    return "\n".join(lines)

def categorize(commits):
    buckets = {key: [] for key, _ in SECTION_ORDER}
    buckets["breaking"] = []
    buckets["other"] = []

    for msg in commits:
        m = COMMIT_REGEX.match(msg)

        # Detect BREAKING CHANGE footer
        breaking_footer = (
            "BREAKING CHANGE:" in msg
            or "BREAKING-CHANGE:" in msg
            or "BREAKING CHANGES:" in msg
        )

        if m:
            t = m.group("type")
            scope = m.group("scope")
            message = m.group("message")
            is_breaking = bool(m.group("breaking")) or breaking_footer

            full = f"{scope}: {message}" if scope else message

            if is_breaking:
                buckets["breaking"].append(full)
            else:
                buckets[t].append(full)
        else:
            # Non‑conventional commit
            if breaking_footer:
                buckets["breaking"].append(msg)
            else:
                buckets["other"].append(msg)

    return buckets

def generate_section(title, items):
    if not items:
        return ""
    lines = [f"### {title}", ""]
    lines.extend(f"- {item}" for item in items)
    lines.append("")
    return "\n".join(lines)

def bump_version(version: str, has_breaking: bool, has_features: bool) -> str:
    """Return a new version string bumped according to semantic versioning."""
    major, minor, patch = map(int, version.split("."))

    if has_breaking:
        major += 1
        minor = 0
        patch = 0
    elif has_features:
        minor += 1
        patch = 0
    else:
        patch += 1

    return f"{major}.{minor}.{patch}"

def update_pyproject_version(new_version: str, pyproject_path: Path = Path("pyproject.toml")):
    """Write the new version back into pyproject.toml."""
    data = tomllib.loads(pyproject_path.read_text())

    if "project" not in data:
        raise KeyError("Missing [project] section in pyproject.toml")

    data["project"]["version"] = new_version

    # Write TOML back manually (tomllib is read-only)
    lines = pyproject_path.read_text().splitlines()
    new_lines = []

    for line in lines:
        if line.strip().startswith("version"):
            new_lines.append(f'version = "{new_version}"')
        else:
            new_lines.append(line)

    pyproject_path.write_text("\n".join(new_lines))


def write_changelog(release_mode=False):
    
    tags = get_tags()
    if not tags:
        raise RuntimeError("No tags found. Cannot generate multi-release changelog.")

    version = get_version_from_pyproject()
    lines = [TEMPLATE_HEADER]

    # -------------------------
    # UNRELEASED SECTION
    # -------------------------
    latest_tag = tags[-1]
    unreleased_commits = get_unreleased_commits(latest_tag)
    unreleased_buckets = categorize(unreleased_commits)

    if release_mode:
        # Automated release: convert Unreleased → real release
        today = date.today().isoformat()
        lines.append(f"## [v{version}] - {today}\n")

        # Breaking changes first
        breaking_section = generate_breaking_section(unreleased_buckets.get("breaking", []))
        if breaking_section:
            lines.append(breaking_section)

        # Normal sections
        for key, title in SECTION_ORDER:
            section = generate_section(title, unreleased_buckets.get(key, []))
            if section:
                lines.append(section)

        # Other uncategorized commits
        if unreleased_buckets["other"]:
            lines.append(generate_section("Other", unreleased_buckets["other"]))

    else:
        # Normal mode: Unreleased stays manual
        lines.append(f"## [{version} — <Unreleased::Add release date manually: YYYY-MM-DD>]\n")

        breaking_section = generate_breaking_section(unreleased_buckets.get("breaking", []))
        if breaking_section:
            lines.append(breaking_section)

        for key, title in SECTION_ORDER:
            section = generate_section(title, unreleased_buckets.get(key, []))
            if section:
                lines.append(section)

        if unreleased_buckets["other"]:
            lines.append(generate_section("Other", unreleased_buckets["other"]))

    # -------------------------
    # RELEASED TAGS (newest first)
    # -------------------------
    for tag in reversed(tags):
        idx = tags.index(tag)
        previous = tags[idx - 1] if idx > 0 else None

        commits = get_commits_between(previous, tag)
        buckets = categorize(commits)

        tag_date = run_git(["log", "-1", "--format=%as", tag])

        lines.append(f"## [{tag}] - {tag_date}\n")

        # Breaking changes first
        breaking_section = generate_breaking_section(buckets.get("breaking", []))
        if breaking_section:
            lines.append(breaking_section)

        # Normal sections
        for key, title in SECTION_ORDER:
            section = generate_section(title, buckets.get(key, []))
            if section:
                lines.append(section)

        # Other uncategorized commits
        if buckets["other"]:
            lines.append(generate_section("Other", buckets["other"]))

    CHANGELOG.write_text("\n".join(lines).strip() + "\n")
    
RELEASE_NOTES_TEMPLATE = """
# Release {version}

## Summary
This release includes {feature_count} new features, {fix_count} fixes, and {breaking_count} breaking changes.

## Breaking Changes
{breaking_section}

## Features
{feature_section}

## Fixes
{fix_section}

## Documentation
{docs_section}

## Refactoring
{refactor_section}

## Tests
{test_section}

## Chores
{chore_section}

## Other
{other_section}
""".strip()

def generate_release_notes(version: str, buckets: dict) -> str:
    """Generate release notes text from categorized commit buckets."""

    def section(items):
        return "\n".join(f"- {item}" for item in items) if items else "None"

    return RELEASE_NOTES_TEMPLATE.format(
        version=version,
        feature_count=len(buckets["feat"]),
        fix_count=len(buckets["fix"]),
        breaking_count=len(buckets["breaking"]),
        breaking_section=section(buckets["breaking"]),
        feature_section=section(buckets["feat"]),
        fix_section=section(buckets["fix"]),
        docs_section=section(buckets["docs"]),
        refactor_section=section(buckets["refactor"]),
        test_section=section(buckets["test"]),
        chore_section=section(buckets["chore"]),
        other_section=section(buckets["other"]),
    )

def dry_run_preview():
    tags = get_tags()
    latest_tag = tags[-1]

    unreleased_commits = get_unreleased_commits(latest_tag)
    unreleased_buckets = categorize(unreleased_commits)

    has_breaking = bool(unreleased_buckets["breaking"])
    has_features = bool(unreleased_buckets["feat"])

    old_version = get_version_from_pyproject()
    new_version = bump_version(old_version, has_breaking, has_features)

    print("\n=== DRY RUN ===")
    print(f"Current version: {old_version}")
    print(f"Breaking changes detected: {has_breaking}")
    print(f"Features detected: {has_features}")
    print(f"New version would be: {new_version}")

    print("\n--- Release Notes Preview ---\n")
    print(generate_release_notes(new_version, unreleased_buckets))
    print("\n--- End Release Notes Preview ---\n")

    print("Changelog would be updated, but no files will be modified.")
    print("No git tag will be created.")
    print("=== END DRY RUN ===\n")

def write_release_notes_file(version: str, notes: str):
    """Write release notes to a versioned markdown file."""
    out_dir = Path("docs/releases/notes")
    out_dir.mkdir(exist_ok=True)

    file_path = out_dir / f"{version}.md"
    file_path.write_text(notes)

    print(f"Release notes written to {file_path}")

def parse_args():
    parser = argparse.ArgumentParser(description="Generate or release changelog.")
    parser.add_argument(
        "--release",
        action="store_true",
        help="Convert Unreleased section into a new release."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate a release without modifying files or creating tags."
    )
    return parser.parse_args()

def main():
    args = parse_args()

    if args.dry_run:
        dry_run_preview()
        return

    if args.release:
        tags = get_tags()
        latest_tag = tags[-1]
        unreleased_commits = get_unreleased_commits(latest_tag)
        unreleased_buckets = categorize(unreleased_commits)

        has_breaking = bool(unreleased_buckets["breaking"])
        has_features = bool(unreleased_buckets["feat"])

        old_version = get_version_from_pyproject()
        new_version = bump_version(old_version, has_breaking, has_features)

        update_pyproject_version(new_version)
        
        # Generate release notes
        release_notes = generate_release_notes(new_version, unreleased_buckets)
        print("\n--- Release Notes ---\n")
        print(release_notes)
        print("\n--- End Release Notes ---\n")
        
        # Write to file
        write_release_notes_file(new_version, release_notes)
        write_changelog(release_mode=True)

        print(f"Release completed. Version bumped {old_version} → {new_version}.")
    else:
        write_changelog(release_mode=False)
        print("CHANGELOG.md regenerated (Unreleased mode).")

if __name__ == "__main__":
    
    main()
